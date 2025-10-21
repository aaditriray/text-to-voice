# Text-to-Voice Conversation Generator

This Python script converts text-based conversations into spoken dialogue using text-to-speech technology. It's designed to process conversations between two speakers (Agent and Member) and generate a natural-sounding audio file.

## Features

- Converts text conversations to spoken dialogue
- Uses different voices for different speakers (Agent/Member)
- Maintains natural conversation flow
- Supports long conversations
- Combines all audio into a single file

## Requirements

- Python 3.12 or higher
- pyttsx3 (for text-to-speech)
- FFmpeg (for audio processing)

## Installation

1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install pyttsx3
   ```
3. Install FFmpeg:
   - Windows: Download from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
   - Add FFmpeg to your system PATH

## Usage

1. Prepare your conversation text in the format:
   ```text
   Agent: Hello, how can I help you today?
   Member: I'd like to inquire about my account.
   ```

2. Run the script:
   ```bash
   python main.py
   ```

3. Find the generated audio file in the `conversation_audio` directory

## Configuration

- Speech rate can be adjusted by modifying `engine.setProperty('rate', 160)`
- Volume can be adjusted by modifying `engine.setProperty('volume', 1.0)`
- Voice selection is automatic but can be customized in the code

## License

MIT License
