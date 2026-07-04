# Developer Guide - YouTube Transcript RAG Chrome Extension

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CHROME BROWSER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          CHROME EXTENSION (chrome_extension/)            │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                           │   │
│  │  Content Script (content.js)                             │   │
│  │  └─ Runs on YouTube pages                               │   │
│  │  └─ Extracts video IDs                                  │   │
│  │                                                           │   │
│  │  Popup UI (popup.html/css/js)                            │   │
│  │  └─ Chat interface                                       │   │
│  │  └─ Settings modal for API token                         │   │
│  │  └─ Message display                                      │   │
│  │                                                           │   │
│  │  Service Worker (background.js)                          │   │
│  │  └─ Health checks                                        │   │
│  │  └─ Message routing                                      │   │
│  │                                                           │   │
│  │  Storage (Chrome Storage API)                            │   │
│  │  └─ API token (encrypted)                                │   │
│  │  └─ Backend URL                                          │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓ HTTP                                  │
├─────────────────────────────────────────────────────────────────┤
│                  FASTAPI BACKEND (backend/app.py)                │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  API Endpoints:                                            │  │
│  │  • POST /api/load-transcript  → Fetch & process video    │  │
│  │  • POST /api/ask-question     → Answer questions         │  │
│  │  • POST /api/clear-cache      → Clear cached data        │  │
│  │  • GET /health                → Health check             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Data Processing Pipeline:                                │  │
│  │                                                             │  │
│  │  1. YouTube Transcript API                                │  │
│  │     ↓                                                       │  │
│  │  2. RecursiveCharacterTextSplitter (1000 char chunks)     │  │
│  │     ↓                                                       │  │
│  │  3. HuggingFace Embeddings (BAAI/bge-small-en-v1.5)      │  │
│  │     ↓                                                       │  │
│  │  4. FAISS Vector Store                                    │  │
│  │     ↓                                                       │  │
│  │  5. Similarity Search Retriever (k=4)                     │  │
│  │     ↓                                                       │  │
│  │  6. Qwen LLM (via HuggingFace API)                        │  │
│  │     ↓                                                       │  │
│  │  7. LangChain RAG Chain                                    │  │
│  │     ↓                                                       │  │
│  │  8. Answer sent to popup                                   │  │
│  │                                                             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Chrome Extension Files

#### `manifest.json`

- Extension configuration (Manifest v3)
- Defines permissions and permissions
- Specifies content scripts, background worker
- Declares API endpoints we communicate with

**Key sections:**

```json
{
  "manifest_version": 3,
  "host_permissions": ["https://www.youtube.com/*", "http://localhost:8000/*"],
  "content_scripts": [{ "matches": ["https://www.youtube.com/watch?v=*"] }]
}
```

#### `popup.html` & `popup.css`

- UI for the chat interface
- Settings modal for configuration
- Responsive design (400px width)
- Color scheme: Purple gradient (#667eea to #764ba2)

#### `popup.js`

**Main responsibilities:**

1. Detects current YouTube video ID
2. Manages settings (API token, backend URL)
3. Loads transcript from backend
4. Sends questions and displays answers
5. Handles chat UI interactions

**Flow:**

```
Page load → Load settings → Get video ID → Load transcript → Ready for chat
```

#### `content.js`

- Runs in context of YouTube pages
- Can be used to extract additional page data
- Currently minimal (framework for expansion)

#### `background.js`

- Service worker (required in Manifest v3)
- Health checks to backend
- Message routing between popup and content

### 2. FastAPI Backend (`backend/app.py`)

#### Key Classes & Functions

**Request Models:**

```python
class TranscriptRequest(BaseModel):
    video_id: str
    api_token: str

class QuestionRequest(BaseModel):
    video_id: str
    question: str
    api_token: str
```

**Main Functions:**

```python
def get_youtube_transcript(video_id: str) -> str
  - Uses YouTubeTranscriptApi
  - Extracts English transcript
  - Returns full text

def create_rag_chain(chunks, api_token: str)
  - Creates embeddings
  - Builds FAISS vector store
  - Sets up LLM
  - Returns LangChain RAG chain
```

**API Endpoints:**

| Endpoint               | Method | Purpose                   |
| ---------------------- | ------ | ------------------------- |
| `/health`              | GET    | Health check              |
| `/api/load-transcript` | POST   | Load & process transcript |
| `/api/ask-question`    | POST   | Answer questions          |
| `/api/clear-cache`     | POST   | Clear memory cache        |

#### Data Caching

Transcripts cached in memory:

```python
transcript_cache = {
    "video_id": {
        "transcript": str,      # Full text
        "chunks": list,         # Document chunks
        "chunks_count": int,    # Number of chunks
        "api_token": str,       # For RAG chain
        "chain": RAGChain       # LangChain RAG
    }
}
```

**Benefits:**

- Subsequent questions for same video are instant
- No need to re-fetch transcript
- No need to rebuild FAISS index

---

## Data Flow Example

### Scenario: User asks question about video

**1. User clicks extension → popup opens**

```
popup.js: addEventListener('click', getCurrentVideoId)
```

**2. Extract video ID from URL**

```
popup.js:
- Gets active tab URL
- Extracts video ID using regex
- Displays to user
```

**3. Load transcript**

```javascript
popup.js:
fetch('/api/load-transcript', {
  body: JSON.stringify({
    video_id: "dQw4w9WgXcQ",
    api_token: "hf_xxxx"
  })
})

app.py:
- Check if cached
- If not: fetch from YouTube API
- Split into chunks
- Create embeddings
- Build FAISS index
- Cache everything
- Return to popup
```

**4. User asks question**

```javascript
popup.js:
fetch('/api/ask-question', {
  body: JSON.stringify({
    video_id: "dQw4w9WgXcQ",
    question: "What is this video about?",
    api_token: "hf_xxxx"
  })
})

app.py:
- Get cached transcript data
- Retrieve relevant chunks (FAISS)
- Pass to LLM with prompt
- Get answer
- Return to popup

popup.js:
- Add answer to chat UI
- Scroll to bottom
```

---

## Technology Stack

| Layer             | Technology                   | Purpose                 |
| ----------------- | ---------------------------- | ----------------------- |
| **Frontend**      | Chrome Extension Manifest v3 | Browser integration     |
| **Frontend**      | HTML/CSS/JavaScript          | UI                      |
| **Storage**       | Chrome Storage API           | Settings storage        |
| **Backend**       | FastAPI                      | REST API server         |
| **Backend**       | Python 3.8+                  | Backend language        |
| **Data**          | YouTubeTranscriptApi         | Fetch captions          |
| **Chunking**      | LangChain TextSplitter       | Split documents         |
| **Embeddings**    | HuggingFace (BAAI/bge-small) | Convert text to vectors |
| **Vector DB**     | FAISS                        | Similarity search       |
| **LLM**           | Qwen2.5-7B via HuggingFace   | Question answering      |
| **Orchestration** | LangChain                    | RAG chain setup         |

---

## Customization Guide

### Change LLM Model

Edit `backend/app.py`, around line 110:

```python
# OLD:
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    ...
)

# NEW (e.g., Mistral):
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.1",
    ...
)
```

**Other models to try:**

- `meta-llama/Llama-2-7b-chat-hf` (good quality, slower)
- `google/flan-t5-large` (faster, lower quality)
- `HuggingFaceH4/zephyr-7b-beta` (balanced)

### Change Embedding Model

Edit `backend/app.py`, around line 97:

```python
embedding = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"  # Change this
)
```

**Other models:**

- `sentence-transformers/all-MiniLM-L6-v2` (faster)
- `BAAI/bge-large-en-v1.5` (better quality, slower)

### Change Chunk Size

Edit `backend/app.py`, around line 67:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Change this (bytes)
    chunk_overlap=200     # Change this too
)
```

**Smaller chunks (500):** More specific but more requests  
**Larger chunks (2000):** Faster but less precise

### Change Number of Retrieved Chunks

Edit `backend/app.py`, around line 107:

```python
retriever = vector_store.as_retriever(
    search_kwargs={"k": 4}  # Change this number
)
```

**Lower k (2):** Faster, less context  
**Higher k (8):** Slower, more context

### Add Logging

In `popup.js`, replace:

```javascript
console.error("Error:", error);
```

With:

```javascript
// Send error to backend for logging
fetch(`${backendUrl}/api/log`, {
  method: "POST",
  body: JSON.stringify({ error: error.message }),
});
```

---

## Error Handling

### Backend Errors

| Error                 | Cause                 | Fix                        |
| --------------------- | --------------------- | -------------------------- |
| `TranscriptsDisabled` | Video has no captions | Try different video        |
| `HTTPException 400`   | Invalid video ID      | Check URL format           |
| `HTTPException 500`   | Server error          | Check logs, restart server |
| Timeout               | Too many requests     | Clear cache, restart       |

### Extension Errors

| Error                   | Cause              | Fix                 |
| ----------------------- | ------------------ | ------------------- |
| "Backend not reachable" | Server not running | Run `python app.py` |
| "Invalid API token"     | Wrong HF token     | Get new token       |
| "No transcript loaded"  | Endpoint failed    | Check backend logs  |

---

## Testing

### Test Backend Health

```bash
curl http://localhost:8000/health
```

### Test Transcript Loading

```bash
curl -X POST http://localhost:8000/api/load-transcript \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "api_token": "your_token_here"
  }'
```

### Test Question Answering

```bash
curl -X POST http://localhost:8000/api/ask-question \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "question": "What is this video about?",
    "api_token": "your_token_here"
  }'
```

---

## Performance Optimization

### 1. Caching

- Transcripts cached in memory
- Same video = instant second query
- For many videos, consider database

### 2. Vector Store

- FAISS is in-memory
- Fast similarity search
- Consider persistent storage for production

### 3. Chunking

- Smaller chunks = more API calls but faster
- Larger chunks = fewer calls but slower
- Current: 1000 bytes with 200 overlap (balanced)

### 4. LLM Selection

- Qwen2.5-7B: Good balance of speed/quality
- Larger models: Better quality, slower
- Smaller models: Faster, lower quality

---

## Security Considerations

### 1. API Token Storage

- Stored in Chrome Storage (encrypted at rest)
- Never logged or exposed
- Only sent over HTTPS to HuggingFace

### 2. Backend Server

- Currently open to all origins (CORS)
- For production, restrict to specific domains
- Add authentication if needed

### 3. Data Privacy

- Transcripts stored in server memory only
- Cleared when server restarts
- No persistent database by default

### 4. HTTPS

- Use HTTPS in production
- Chrome extensions work with localhost without HTTPS

---

## Future Enhancements

- [ ] Deploy backend to cloud (Railway, Heroku, AWS)
- [ ] Add database for persistent transcript caching
- [ ] Multi-language support
- [ ] User authentication
- [ ] Rate limiting
- [ ] Chat history export
- [ ] Custom prompt templates
- [ ] Multiple LLM options in UI
- [ ] Sidebar mode instead of popup
- [ ] Video transcript summary generation

---

## Debugging

### Enable Detailed Logging

**Backend:** Edit `app.py` line 11:

```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

**Frontend:** Open DevTools in Chrome

```
F12 → Console tab → See logs from popup.js
F12 → Application tab → See stored settings
```

### Common Issues & Fixes

**Issue: "ModuleNotFoundError: No module named 'langchain'"**

```bash
# Solution:
cd backend
pip install -r requirements.txt
```

**Issue: "Connection refused" to backend**

```bash
# Solution:
# Check backend is running
python app.py  # Should show http://0.0.0.0:8000
```

**Issue: "Invalid HuggingFace token"**

```bash
# Solution:
# Get new token from https://huggingface.co/settings/tokens
# Make sure it has "read" access
```

---

## Questions?

Refer to:

- [LangChain Docs](https://python.langchain.com/)
- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [HuggingFace Docs](https://huggingface.co/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
