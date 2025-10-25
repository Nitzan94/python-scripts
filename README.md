# Python Utilities Collection

Collection of 12+ Python utility scripts with CLI interfaces and a Streamlit web dashboard.

## Features

### 🤖 Script Generator (NEW!)
AI-powered script generation using Claude Agent SDK:
- Describe what you want, Claude generates it
- Follows project patterns (CLI args, error handling, type hints)
- Preview before integration
- Auto-updates dependencies

### 📦 Existing Utilities

**Content Tools:**
- Articles to Audio: Convert web articles to MP3
- YouTube Downloader: Download videos/playlists with quality control
- YouTube Transcript: Download video transcripts (text/SRT/JSON)
- QR Code Tool: Generate and scan QR codes
- Text to Handwriting: Convert text to handwriting images

**File Tools:**
- EXIF Editor: View/strip image metadata
- Resume Parser: Extract data from PDF/DOCX resumes
- Markdown Table Generator: CSV/JSON to markdown tables

**Web Tools:**
- Weather Alert: Weather forecast with alerts
- Browser History: Chrome history to markdown journal

**Data Tools:**
- Meeting Notes: Voice transcription

## Installation

```bash
# Clone repository
git clone https://github.com/Nitzan94/python-scripts.git
cd python-scripts

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)

```bash
# Set up API key for Script Generator (optional)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run Streamlit app
streamlit run app.py
```

Open http://localhost:8502

### Command Line

Each script has full CLI support:

```bash
# Examples
python "QR Code Tool.py" generate "https://example.com"
python "Weather Alert.py" London -k YOUR_API_KEY
python "YouTube Transcript.py" download VIDEO_URL -f srt
python "EXIF Editor.py" strip photo.jpg
```

Run any script with `-h` for help:
```bash
python "script-name.py" -h
```

## Script Generator Setup

1. Get API key from https://console.anthropic.com/
2. Create `.env` file:
   ```bash
   ANTHROPIC_API_KEY=your_key_here
   ```
3. Open Script Generator tab in Streamlit
4. Describe your script
5. Review and approve generated code

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies
- Optional: FFmpeg for video/audio conversion
- Optional: Anthropic API key for Script Generator

## Project Standards

All scripts follow these patterns:
- Two `ABOUTME` file headers
- Type hints on all functions
- Argparse for CLI arguments
- Comprehensive error handling
- ASCII-only output ([OK], [ERROR], [WARN], [INFO])
- Windows-compatible

## Contributing

Generated scripts automatically follow project standards. To add manually:
1. Follow existing script patterns
2. Include file headers, type hints, error handling
3. Add to Streamlit app navigation
4. Update requirements.txt if needed

## License

MIT License
