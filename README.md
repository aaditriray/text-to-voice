# Text-to-Voice Conversation Generator

This Python script converts text-based conversations into spoken dialogue using **Google Text-to-Speech** with **Indian English accent**. It's designed to process conversations between two speakers (Agent and Member) and generate natural-sounding audio files.

## Features

- Converts text conversations to spoken dialogue with **Indian English accent**
- Uses Google Text-to-Speech (gTTS) for high-quality audio
- Processes conversations between Agent and Member speakers
- Maintains natural conversation flow
- Supports long conversations
- Combines all audio segments into a single MP3 file
- Cross-platform compatible (Windows, macOS, Linux)

## Requirements

- Python 3.12 or higher
- FFmpeg (for audio processing and combining segments)
- Internet connection (for Google Text-to-Speech API)

## Installation

### Step 1: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Python Dependencies

```bash
# Option A: Using requirements.txt
pip install -r requirements.txt

# Option B: Using pyproject.toml
pip install -e .
```

### Step 3: Install FFmpeg

- **Windows**: 
  - Download from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
  - Install and add FFmpeg to your system PATH
  - Or use: `choco install ffmpeg` (if using Chocolatey)

- **macOS**: 
  ```bash
  brew install ffmpeg
  ```

- **Linux**: 
  ```bash
  sudo apt-get install ffmpeg
  ```

## Usage

### 1. Prepare Conversation File

Create a `conversation.txt` file in the same directory as `main.py` with the format:
```text
Agent: Good morning, how can I help you today?
Member: Hi, I'd like to inquire about my account.
Agent: Of course, I'd be happy to assist you.
Member: Thank you!
```

### 2. Run the Script

```bash
# Make sure virtual environment is activated
.venv\Scripts\python.exe main.py

# Or after activating venv:
python main.py
```

### 3. Access Generated Audio

The combined audio file will be saved in:
```
conversation_audio/combined_conversation_YYYYMMDD_HHMMSS.mp3
```

## Configuration

The script uses Google Text-to-Speech with the following settings:
- **Language**: English with Indian accent (via `tld='co.in'`)
- **Output Format**: MP3 (44.1 kHz, stereo)
- **Audio Quality**: High (libmp3lame -q:a 2)

Individual audio segments are temporarily stored in `conversation_audio/lines/` and cleaned up after combining.

## Troubleshooting

### ModuleNotFoundError: No module named 'gtts'
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

### FFmpeg not found
- Verify FFmpeg is installed: `ffmpeg -version`
- On Windows, ensure FFmpeg is in your PATH

### No internet connection error
- Google Text-to-Speech requires internet connection
- Ensure you have active internet connectivity

## Project Structure

```
.
├── main.py                 # Main script
├── conversation.txt        # Input conversation file (you create this)
├── pyproject.toml         # Project configuration
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── conversation_audio/    # Output directory (created automatically)
    └── lines/            # Temporary audio segments
```

## License

MIT License
