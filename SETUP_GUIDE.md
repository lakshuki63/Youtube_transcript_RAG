# YouTube Transcript RAG - Chrome Extension Setup Guide

## Quick Start (5 minutes)

### Step 1: Install Backend Dependencies

```bash
cd yt_chatbot_extension/backend
pip install -r requirements.txt
```

### Step 2: Generate Extension Icons

```bash
cd ..
python setup.py
```

(Or manually create 16x16, 48x48, 128x128 PNG icons and save to `chrome_extension/icons/`)

### Step 3: Start Backend Server

```bash
cd backend
python app.py
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

### Step 4: Load Chrome Extension

1. Open `chrome://extensions/` in Chrome
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `chrome_extension` folder
5. Extension appears in your toolbar

### Step 5: Configure Extension

1. Go to any **YouTube video** page
2. Click the extension icon
3. Click **⚙️ Settings**
4. Enter your **HuggingFace API Token**
   - Get free token: https://huggingface.co/settings/tokens
5. Click **Save**

### Step 6: Start Chatting!

1. Refresh the YouTube page
2. Ask questions about the video transcript
3. Get AI-powered answers instantly

---

## Troubleshooting

| Issue                              | Solution                                                   |
| ---------------------------------- | ---------------------------------------------------------- |
| "Backend URL not reachable"        | Make sure `python app.py` is running in backend folder     |
| "Failed to load transcript"        | Video might have disabled captions; try another video      |
| "Extension not showing in toolbar" | Refresh extensions page or restart Chrome                  |
| "No HuggingFace API Token"         | Get free token from https://huggingface.co/settings/tokens |
| "ImportError: No module named PIL" | Run `pip install Pillow` then `python setup.py`            |

---

## File Structure

```
yt_chatbot_extension/
├── chrome_extension/           # Chrome Extension Files
│   ├── manifest.json           # Extension configuration (Manifest v3)
│   ├── popup.html              # Chat interface UI
│   ├── popup.css               # Styling (gradient, chat bubbles, modal)
│   ├── popup.js                # Popup logic (settings, chat, API calls)
│   ├── content.js              # Detects YouTube video IDs
│   ├── background.js           # Service worker (health checks)
│   └── icons/
│       ├── icon-16.png         # Small toolbar icon
│       ├── icon-48.png         # Medium icon
│       └── icon-128.png        # Large icon
├── backend/                    # FastAPI Backend
│   ├── app.py                  # Main server
│   │   ├── /health             # Health check
│   │   ├── /api/load-transcript    # Load & process transcript
│   │   └── /api/ask-question   # Answer questions
│   └── requirements.txt         # Python dependencies
├── setup.py                    # Icon generator script
└── README.md                   # Full documentation
```

---

## How It Works

### Extension Flow

```
YouTube Page
    ↓
Content Script (extract video ID)
    ↓
Popup Shows Chat Interface
    ↓
User configures API token (popup.js)
    ↓
Backend API call to /api/load-transcript
    ↓
Backend fetches YouTube transcript
    ↓
User asks question
    ↓
Backend RAG chain processes question
    ↓
Answer returned to popup
    ↓
Displayed in chat bubble
```

### Backend Processing

```
1. Fetch Transcript (youtube-transcript-api)
2. Split into chunks (RecursiveCharacterTextSplitter)
3. Create embeddings (HuggingFace)
4. Build FAISS vector store
5. Create retriever (similarity search)
6. Setup Qwen LLM via HuggingFace
7. Build RAG chain (LangChain)
8. Answer questions using retrieved context
```

---

## Customization

### Change LLM Model

Edit `backend/app.py`, line ~110:

```python
repo_id="Qwen/Qwen2.5-7B-Instruct"  # Change this
```

Other options:

- `meta-llama/Llama-2-7b-chat-hf`
- `mistralai/Mistral-7B-Instruct-v0.1`
- `google/flan-t5-large`

### Change Embedding Model

Edit `backend/app.py`, line ~97:

```python
model_name="BAAI/bge-small-en-v1.5"  # Change this
```

### Change Chunk Size

Edit `backend/app.py`, line ~67:

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```

### Change Retriever Search Results

Edit `backend/app.py`, line ~107:

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 4})  # Change k value
```

---

## API Reference

### POST /api/load-transcript

Load and process YouTube transcript

**Request:**

```json
{
  "video_id": "dQw4w9WgXcQ",
  "api_token": "hf_xxxxxxxxxxxx"
}
```

**Response:**

```json
{
  "video_id": "dQw4w9WgXcQ",
  "transcript": "full transcript text...",
  "chunks_count": 42
}
```

### POST /api/ask-question

Answer a question about loaded transcript

**Request:**

```json
{
  "video_id": "dQw4w9WgXcQ",
  "question": "What is this video about?",
  "api_token": "hf_xxxxxxxxxxxx"
}
```

**Response:**

```json
{
  "video_id": "dQw4w9WgXcQ",
  "question": "What is this video about?",
  "answer": "This video is about..."
}
```

---

## Performance Tips

1. **Cache**: Transcripts are cached in memory. Refresh with same video ID = instant response
2. **Chunk Size**: Larger chunks = fewer API calls but less precise. Tweak in `app.py`
3. **Vector Store**: FAISS is loaded in memory. For many videos, consider SQLite/PostgreSQL
4. **LLM**: Qwen2.5-7B is fast. For better quality, use larger models (takes longer)

---

## Next Steps

- [ ] Deploy backend to cloud (Heroku, AWS, DigitalOcean)
- [ ] Add multi-language support
- [ ] Add chat history export
- [ ] Create sidebar mode instead of popup
- [ ] Add summary generation
- [ ] Setup database for persistent cache
- [ ] Add user authentication
- [ ] Rate limiting for API

---

## Support & Issues

- **Chrome Extension Issues**: Check [Chrome Extensions Docs](https://developer.chrome.com/docs/extensions/)
- **LangChain Issues**: Check [LangChain Docs](https://python.langchain.com/)
- **YouTube API Issues**: Check [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)
- **HuggingFace Issues**: Check [HuggingFace Docs](https://huggingface.co/docs)

---

Enjoy chatting with YouTube videos! 🎬💬


<!-- .\.venv\Scripts\Activate.ps1 -->