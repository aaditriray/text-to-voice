
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

# Full transcript text
transcript = """Agent: Good morning, you're through to Alpha Insurance, Olivia speaking. How can I help you today?
Member: Hi Olivia, I’m hoping to get a retirement quotation for my pension. I’m planning to retire early next year and just want to understand what my options look like.
Agent: Of course, Mr. Thompson. I’d be happy to help with that. Before we proceed, I’ll need to complete a quick identity verification. Is that alright?
Member: Yes, go ahead.
Agent: Thank you. Can I start by taking your full name, date of birth, and postcode, please?
Member: Sure. It’s David Thompson, born 12th March 1964, and my postcode is BN3 5QT.
Agent: Perfect, thank you. And just to confirm, are you calling about your Personal Pension Plan with Alpha Insurance?
Member: Yes, that’s correct.
Agent: Great. I’ll now ask you a couple of security questions to verify your identity. Can you please confirm the last four digits of your National Insurance number?
Member: It’s 7421.
Agent: Thank you. And could you tell me the approximate value of your pension fund as of your last statement?
Member: I believe it was around £185,000.
Agent: That matches our records. Thank you for confirming. You’ve been successfully verified.
Member: Brilliant.
Agent: Now, to help us prepare your retirement quotation, I’ll need a few more details. Are you planning to take your pension as a lump sum, regular income, or a combination of both?
Member: I’m leaning towards a combination. I’d like to take a lump sum to clear my mortgage and then draw a monthly income.
Agent: Understood. And when are you hoping to retire?
Member: Ideally, by April next year—so around the start of the new tax year.
Agent: Got it. And do you have any other pension pots or retirement income sources we should be aware of when preparing your quotation?
Member: Just a small workplace pension, but I’d prefer to keep that separate for now.
Agent: No problem. Thank you for sharing that. Based on what you’ve told me, I’ll now pass this information to one of our retirement specialists. They’ll prepare a tailored quotation and give you a call back within the next 3–5 working days. Is there a preferred time for them to reach you?
Member: Afternoons are best—anytime after 2 PM.
Agent: Noted. And just to confirm, we’ll call you on the number you’re using now?
Member: Yes, that’s fine.
Agent: Perfect. Is there anything else I can help you with today?
Member: No, that’s everything. Thanks for your help, Olivia.
Agent: You’re very welcome, Mr. Thompson. I hope the quotation gives you a clear picture of your retirement options. Wishing you a smooth transition into retirement. Take care and goodbye for now.
Member: Thanks, goodbye.
"""

# Create output directory if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, 'conversation_audio')
os.makedirs(output_dir, exist_ok=True)

print("\nDebug Info:")
print(f"Script directory: {script_dir}")
print(f"Output directory: {output_dir}")

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
            timeout = 30
            start_time = time.time()
            while not os.path.exists(current_file):
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Timeout waiting for file: {current_file}")
                time.sleep(0.1)
                print(".", end="", flush=True)
            
            # Verify the file size
            file_size = os.path.getsize(current_file)
            if file_size == 0:
                print(f"\nWarning: Generated file is empty: {current_file}")
                continue
            
            print(f"\nDebug: File created successfully: {current_file} (size: {file_size} bytes)")
            conversation_parts.append(current_file)
        
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("\n⚠️ FFmpeg not found. Cannot combine audio files.")
            print("Please ensure FFmpeg is installed and in your system PATH.")
            print("You can download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/")
            raise Exception("FFmpeg not found. Audio files cannot be combined.")

        # Create the concat file for direct concatenation
        concat_list = os.path.join(lines_dir, 'concat_list.txt')
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


# Process the conversation
try:
    output_file = process_conversation(transcript, engine, male_voice, female_voice, output_dir)
    print(f"\n✅ Successfully created conversation audio: {os.path.basename(output_file)}")
except Exception as e:
    print(f"\n❌ Error during audio processing: {str(e)}")
finally:
    # Always try to stop the engine properly
    try:
        engine.stop()
    except:
        pass