# AI Podcast Generator

An AI-powered podcast generation system that converts text into multi-voice audio content with dynamic configuration options.

## Features

- Text-to-speech conversion using Edge TTS
- Multiple voice styles (male, female, child)
- Multi-host configuration
- Background music support
- Content from text or URL
- Real-time podcast generation
- In-browser audio playback

## Requirements

- Python 3.12+
- FastAPI
- Edge TTS
- OpenAI API key
- Other dependencies in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ai_podcast_workflow
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create and configure .env file:
```env
OPENAI_API_KEY=your_openai_api_key_here
HOST=127.0.0.1
PORT=8000
STATIC_DIR=./static
AUDIO_DIR=./audio
OUTPUT_DIR=./output
TEMP_DIR=./temp
DEBUG=True
```

4. Run the application:
```bash
python -m uvicorn main:app --reload
```

## API Endpoints

- `GET /`: Web interface
- `POST /create_podcast`: Generate podcast
  - Request body:
    ```json
    {
      "config": {
        "hosts": [
          {
            "gender": "male|female|child"
          }
        ],
        "background_music": true
      },
      "content": {
        "text": "Your content here",
        "url": "https://example.com"
      }
    }
    ```

## Project Structure

```
ai_podcast_workflow/
├── main.py              # FastAPI application
├── static/              # Static files
│   ├── index.html      # Web interface
│   ├── script.js       # Frontend logic
│   └── styles.css      # Styling
├── audio/              # Generated audio files
├── output/             # Output directory
├── temp/               # Temporary files
└── requirements.txt    # Python dependencies
```

## License

MIT License
