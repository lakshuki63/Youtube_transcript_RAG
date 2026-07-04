# YouTube Transcript RAG Chrome Extension

A Chrome extension that allows you to chat with YouTube video transcripts using LangChain RAG (Retrieval-Augmented Generation).

## Features

- Automatically detects YouTube videos
- Interactive chat interface in a popup
- Retrieves relevant transcript sections
- Uses Qwen LLM for intelligent responses
- Secure HuggingFace API token management
- Local backend server for processing

## Project Structure

```
yt_chatbot_extension/
├── chrome_extension/          # Chrome extension files
│   ├── manifest.json          # Extension configuration
│   ├── popup.html             # Chat interface
│   ├── popup.css              # Styling
│   ├── popup.js               # Popup logic
│   ├── content.js             # Content script
│   ├── background.js          # Service worker
│   └── icons/                 # Extension icons
├── backend/                   # FastAPI backend server
│   ├── app.py                 # Main server application
│   └── requirements.txt        # Python dependencies
└── README.md
```

## Installation & Setup

### 1. Backend Setup

Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Run the backend server:

```bash
python app.py
```

The server will start at `http://localhost:8000`

Health check: `http://localhost:8000/health`

### 2. Chrome Extension Setup

1. Open `chrome://extensions/` in your Chrome browser
2. Enable "Developer mode" (top right corner)
3. Click "Load unpacked"
4. Navigate to the `chrome_extension` folder and select it
5. The extension should now appear in your extensions list

### 3. Configure the Extension

1. Go to any YouTube video page
2. Click the extension icon 
3. Click the settings button 
4. Enter your HuggingFace API token (get one from [here](https://huggingface.co/settings/tokens))
5. Keep the backend URL as `http://localhost:8000` (or change if running elsewhere)
6. Click "Save"

## Usage

1. Open any YouTube video page
2. Click the extension popup
3. Wait for the transcript to load
4. Ask any question about the video content
5. The AI will provide answers based on the transcript

## How It Works

1. **Content Script**: Detects YouTube video pages and extracts video IDs
2. **Backend Server**:
   - Fetches YouTube transcripts using `youtube-transcript-api`
   - Splits transcripts into chunks for better processing
   - Creates FAISS vector embeddings using HuggingFace embeddings
   - Uses LangChain RAG to retrieve relevant sections
   - Sends responses to the extension
3. **Extension Popup**:
   - Displays chat interface
   - Manages user settings
   - Communicates with backend via HTTP requests

## API Endpoints

### `GET /health`

Health check endpoint

### `POST /api/load-transcript`

Load and process YouTube transcript

```json
{
  "video_id": "dQw4w9WgXcQ",
  "api_token": "your_huggingface_token"
}
```

### `POST /api/ask-question`

Ask a question about the loaded transcript

```json
{
  "video_id": "dQw4w9WgXcQ",
  "question": "What is this video about?",
  "api_token": "your_huggingface_token"
}
```

### `POST /api/clear-cache`

Clear cached transcripts

## Requirements

- Python 3.8+
- Chrome browser
- HuggingFace API token (free)
- Internet connection

## Troubleshooting

### "Backend URL not reachable"

- Ensure `python app.py` is running in the backend folder
- Check that the URL in settings matches your backend URL
- Default should be `http://localhost:8000`

### "Failed to load transcript"

- Some videos have disabled transcripts
- Try a different video
- Check HuggingFace API token is valid

### "Extension not appearing"

- Refresh the extensions page
- Try reloading the extension
- Check browser console for errors (F12 → Extensions tab)

## Future Enhancements

- [ ] Multi-language transcript support
- [ ] Sidebar integration instead of popup
- [ ] Transcript summary generation
- [ ] Save chat history
- [ ] Multiple LLM options
- [ ] Cloud deployment guide
- [ ] User authentication
- [ ] Rate limiting

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, refer to:

- [LangChain Documentation](https://python.langchain.com/)
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)
- [Chrome Extensions Docs](https://developer.chrome.com/docs/extensions/)
