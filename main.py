# -*- coding: utf-8 -*-
import pyttsx3
import os
import time
import subprocess
from datetime import datetime

def queue_audio_segment(engine, text, voice_id, output_file):
    """Queue an audio segment for generation"""
    try:
        print(f"Queuing audio generation for: {output_file}")
        engine.setProperty('voice', voice_id)
        engine.save_to_file(text, output_file)
    except Exception as e:
        print(f"\nError queuing audio segment: {str(e)}")
        raise

def check_ffmpeg():
    """Check if FFmpeg is properly installed"""
    try:
        # Try to import pydub and check ffmpeg
        from pydub.utils import which
        ffmpeg_path = which("ffmpeg")
        if ffmpeg_path is None:
            print("❌ FFmpeg not found in system PATH")
            return False
        print(f"✅ FFmpeg found at: {ffmpeg_path}")
        return True
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {str(e)}")
        return False

def wait_for_file(output_file, timeout=30):
    """Wait for a file to be created with timeout"""
    start_time = time.time()
    while not os.path.exists(output_file):
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout waiting for file: {output_file}")
        time.sleep(0.1)
        print(".", end="", flush=True)
    print(f"\nFile created successfully: {output_file}")
    
    # Verify file size
    file_size = os.path.getsize(output_file)
    if file_size == 0:
        raise Exception(f"File was created but is empty: {output_file}")
    print(f"File size: {file_size} bytes")

def read_conversation(file_path):
    """Read conversation from a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading conversation file: {str(e)}")
        raise

def process_conversation(transcript, engine, male_voice, female_voice, output_dir):
    """Process the conversation and create audio files"""
    # Generate timestamped filename for the conversation
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    conversation_parts = []
    lines_dir = os.path.join(output_dir, 'lines')
    output_file = os.path.join(output_dir, f'combined_conversation_{timestamp}.mp3')
    concat_list = os.path.join(lines_dir, 'concat_list.txt')
    
    try:
        # Create a directory for individual lines
        os.makedirs(lines_dir, exist_ok=True)
        print("\nProcessing conversation line by line...")
        
        # Start the event loop
        engine.startLoop(False)  # Start in async mode
        
        # Process each line individually
        line_number = 0
        for line in transcript.strip().split('\n'):
            if not line:
                continue
                
            line_number += 1
            current_file = os.path.join(lines_dir, f'line_{line_number:03d}.mp3')
            
            print(f"\nDebug: Processing line {line_number}: {line[:50]}...")  # Show first 50 chars of line
            
            if not line.strip():
                print("Debug: Skipping empty line")
                continue
                
            if line.startswith('Agent:'):
                print(f"\nProcessing Agent line {line_number}...")
                try:
                    engine.setProperty('voice', female_voice.id)
                    text = line.replace('Agent:', '').strip()
                    if not text:
                        print(f"Debug: Empty text after processing line {line_number}")
                        continue
                    print(f"Debug: Agent text to process: {text[:50]}...")
                    engine.save_to_file(text, current_file)
                except Exception as e:
                    print(f"Error processing Agent line {line_number}: {str(e)}")
                    raise
            elif line.startswith('Member:'):
                print(f"\nProcessing Member line {line_number}...")
                try:
                    engine.setProperty('voice', male_voice.id)
                    text = line.replace('Member:', '').strip()
                    if not text:
                        print(f"Debug: Empty text after processing line {line_number}")
                        continue
                    print(f"Debug: Member text to process: {text[:50]}...")
                    engine.save_to_file(text, current_file)
                except Exception as e:
                    print(f"Error processing Member line {line_number}: {str(e)}")
                    raise
            else:
                print(f"Debug: Skipping line {line_number} - doesn't start with Agent: or Member:")
                continue
                
            print(f"Debug: Processing line {line_number}")
            
            # Use iterate instead of runAndWait to avoid deadlocks
            engine.iterate()
            
            # Wait for file to be created
            print(f"Debug: Waiting for file to be created: {current_file}")
            try:
                wait_for_file(current_file, 30)
                conversation_parts.append(current_file)
            except Exception as e:
                print(f"\nError waiting for file {current_file}: {str(e)}")
                raise
                
        # Combine all parts using FFmpeg
        print("\nPreparing to combine all audio segments...")
        
        # Create concat file for FFmpeg
        with open(concat_list, 'w') as f:
            # Simply write all files in order without any silence
            for audio_file in conversation_parts:
                f.write(f"file '{audio_file.replace(os.sep, '/')}'\n")
        
        # Combine all files
        print("\nCombining all audio segments...")
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_list,
            '-c:a', 'libmp3lame', '-q:a', '2',
            output_file
        ], capture_output=True, check=True)
        
        print("\n✅ Successfully combined all audio segments!")
        print(f"Combined file: {os.path.basename(output_file)}")
        
        # Clean up individual files
        print("\nCleaning up temporary files...")
        for file in conversation_parts + [concat_list]:
            try:
                os.remove(file)
            except:
                pass
        try:
            os.rmdir(lines_dir)
        except:
            pass
            
        return output_file
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        raise
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        raise
    finally:
        # Clean up the engine
        try:
            engine.endLoop()
        except:
            pass
            
        # Try to clean up if anything goes wrong
        try:
            for file in conversation_parts:
                if os.path.exists(file):
                    os.remove(file)
            if os.path.exists(lines_dir):
                os.rmdir(lines_dir)
        except:
            pass

def main():
    # Initialize the TTS engine with a new driver
    engine = pyttsx3.init()

    # Set base properties
    engine.setProperty('rate', 160)  # Speed of speech
    engine.setProperty('volume', 1.0)  # Volume

    # Make sure any previous loops are stopped
    try:
        engine.endLoop()
    except:
        pass

    # Get available voices
    voices = engine.getProperty('voices')

    # Find a male and female voice
    male_voice = None
    female_voice = None

    # Print available voices and select appropriate ones
    print("Available voices:")
    for voice in voices:
        print(f"ID: {voice.id}, Name: {voice.name}, Languages: {voice.languages}, Gender: {voice.gender}")
        # Try to find English voices
        if "en" in str(voice.languages).lower():
            if voice.gender == 'VoiceGenderMale' and not male_voice:
                male_voice = voice
            elif voice.gender == 'VoiceGenderFemale' and not female_voice:
                female_voice = voice

    if not male_voice:
        male_voice = voices[0]  # Fallback to first voice
    if not female_voice:
        female_voice = voices[-1]  # Fallback to last voice

    print(f"\nSelected voices:")
    print(f"Agent (Female): {female_voice.name}")
    print(f"Member (Male): {male_voice.name}")

    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'conversation_audio')
    os.makedirs(output_dir, exist_ok=True)

    # Read transcript from file
    transcript_file = os.path.join(script_dir, 'conversation.txt')
    if not os.path.exists(transcript_file):
        print(f"Error: Conversation file not found: {transcript_file}")
        print("Please create a conversation.txt file in the same directory as this script.")
        exit(1)

    # Read the transcript
    transcript = read_conversation(transcript_file)

    # Verify that the transcript is not empty
    if not transcript.strip():
        print("Error: Conversation file is empty")
        exit(1)

    print("\nSuccessfully loaded conversation from file.")
    print("\nDebug Info:")
    print(f"Script directory: {script_dir}")
    print(f"Output directory: {output_dir}")

    try:
        output_file = process_conversation(transcript, engine, male_voice, female_voice, output_dir)
        print(f"\n✅ Successfully created: {output_file}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()