# -*- coding: utf-8 -*-
from gtts import gTTS
import os
import subprocess
from datetime import datetime

def generate_audio_segment(text, lang='en', tld='co.in', output_file='temp.mp3'):
    """Generate audio using Google Text-to-Speech with Indian accent"""
    try:
        print(f"Generating audio segment: {output_file}")
        # lang='en' with tld='co.in' gives Indian English accent
        tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
        tts.save(output_file)
        print(f"Audio saved: {output_file}")
    except Exception as e:
        print(f"\nError generating audio segment: {str(e)}")
        raise

def check_ffmpeg():
    """Check if FFmpeg is properly installed"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is installed and working")
            return True
        else:
            print("❌ FFmpeg is not properly installed")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in system PATH")
        return False
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {str(e)}")
        return False

def wait_for_file(output_file, timeout=10):
    """Wait for a file to be created with timeout"""
    import time
    start_time = time.time()
    while not os.path.exists(output_file):
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout waiting for file: {output_file}")
        time.sleep(0.1)
    
    # Verify file size
    file_size = os.path.getsize(output_file)
    if file_size == 0:
        raise Exception(f"File was created but is empty: {output_file}")
    print(f"File created successfully: {output_file} ({file_size} bytes)")

def read_conversation(file_path):
    """Read conversation from a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading conversation file: {str(e)}")
        raise

def process_conversation(transcript, output_dir):
    """Process the conversation and create audio files with Indian accent"""
    # Generate timestamped filename for the conversation
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    conversation_parts = []
    lines_dir = os.path.join(output_dir, 'lines')
    output_file = os.path.join(output_dir, f'combined_conversation_{timestamp}.mp3')
    concat_list = os.path.join(lines_dir, 'concat_list.txt')
    
    try:
        # Create a directory for individual lines
        os.makedirs(lines_dir, exist_ok=True)
        print("\nProcessing conversation line by line with Indian English accent...")
        
        # Process each line individually
        line_number = 0
        for line in transcript.strip().split('\n'):
            if not line.strip():
                continue
                
            line_number += 1
            current_file = os.path.join(lines_dir, f'line_{line_number:03d}.mp3')
            
            print(f"\nProcessing line {line_number}: {line[:60]}...")
            
            try:
                # Extract text (remove speaker prefix)
                if line.startswith('Agent:'):
                    text = line.replace('Agent:', '').strip()
                elif line.startswith('Member:'):
                    text = line.replace('Member:', '').strip()
                else:
                    print(f"Skipping line {line_number} - doesn't start with Agent: or Member:")
                    continue
                
                if not text:
                    print(f"Skipping empty text for line {line_number}")
                    continue
                
                # Generate audio with Indian English accent (gTTS with co.in TLD)
                generate_audio_segment(text, lang='en', tld='co.in', output_file=current_file)
                
                # Wait for file to be created
                wait_for_file(current_file, 10)
                conversation_parts.append(current_file)
                
            except Exception as e:
                print(f"Error processing line {line_number}: {str(e)}")
                raise
                
        # Combine all parts using FFmpeg
        print("\nPreparing to combine all audio segments...")
        
        # Create concat file for FFmpeg
        with open(concat_list, 'w') as f:
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
        
        return output_file
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        raise
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        raise
    finally:
        # Try to clean up temporary files
        try:
            if os.path.exists(lines_dir):
                import shutil
                shutil.rmtree(lines_dir)
        except:
            pass

def main():
    # Check FFmpeg installation
    if not check_ffmpeg():
        print("Please install FFmpeg to continue")
        exit(1)
    
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

    print("✅ Successfully loaded conversation from file.")
    print("\n📋 Processing with Indian English accent (using Google Text-to-Speech)")
    print(f"Script directory: {script_dir}")
    print(f"Output directory: {output_dir}")

    try:
        output_file = process_conversation(transcript, output_dir)
        print(f"\n✅ Successfully created: {output_file}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()