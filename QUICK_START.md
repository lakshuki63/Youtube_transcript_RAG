# ⚡ QUICK START - YouTube Transcript RAG Chrome Extension

Follow these steps to get up and running in **5 minutes**.

## Prerequisites

- Chrome browser
- Python 3.8+
- Free HuggingFace API token (get from https://huggingface.co/settings/tokens)

---

## 🚀 Installation Steps

### Step 1: Install Dependencies (1 minute)

Open PowerShell in the `backend` folder and run:

```powershell
pip install -r requirements.txt
```

**If you get errors:**

- Make sure Python is installed: `python --version`
- Update pip: `python -m pip install --upgrade pip`

### Step 2: Generate Extension Icons (optional, 30 seconds)

In the root folder (`yt_chatbot_extension`), run:

```powershell
python setup.py
```

This creates icon files in `chrome_extension/icons/`

### Step 3: Start Backend Server (1 minute)

Run this command in the `backend` folder:

```powershell
python app.py
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✓ Leave this running!** (Don't close the terminal)

### Step 4: Load Chrome Extension (1 minute)

1. Open Chrome and go to `chrome://extensions/`
2. Enable **"Developer mode"** (toggle in top right corner)
3. Click **"Load unpacked"** button
4. Navigate to and select the **`chrome_extension`** folder
5. The extension should appear in your toolbar with an icon 📺

### Step 5: Configure Extension (1 minute)

1. Go to any **YouTube video** page
2. Click the extension icon in your toolbar
3. A popup appears - click **⚙️ Settings** button
4. Paste your **HuggingFace API token** (get free token here: https://huggingface.co/settings/tokens)
5. Backend URL should be `http://localhost:8000`
6. Click **Save**

### Step 6: Start Chatting! 🎉

1. **Refresh** the YouTube page
2. Wait for "✓ Transcript loaded" message
3. Type your question about the video
4. Get AI-powered answers instantly!

---

## 🎯 Example Questions

Ask any of these about the YouTube video:

- "What is this video about?"
- "Summarize the key points"
- "What are the main topics discussed?"
- "Who are the people mentioned?"
- "What time does topic X start?"

---

## ❌ Troubleshooting

| Problem                               | Solution                                                       |
| ------------------------------------- | -------------------------------------------------------------- |
| **"Failed to load transcript"**       | Some videos have disabled captions. Try a different video.     |
| **"Backend URL not reachable"**       | Make sure `python app.py` is still running in the terminal.    |
| **"Please configure settings first"** | Click the ⚙️ Settings button and enter your HF API token.      |
| **Extension not showing**             | Refresh `chrome://extensions/` or restart Chrome.              |
| **"No module named fastapi"**         | Run `pip install -r requirements.txt` again in backend folder. |
| **"TranscriptsDisabled" error**       | Video doesn't have captions enabled. Try another video.        |

---

## 📁 Folder Structure

```
yt_chatbot_extension/
├── chrome_extension/           ← Load this in Chrome
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.css
│   ├── popup.js
│   ├── content.js
│   ├── background.js
│   └── icons/
├── backend/                    ← Run python app.py here
│   ├── app.py
│   └── requirements.txt
├── setup.py                    ← Run this first
├── start_backend.bat           ← Click to start server (Windows)
├── QUICK_START.md             ← This file
└── README.md                  ← Full documentation
```

---

## 🆘 Help & Support

**Errors?**

1. Check you're in the right folder
2. Make sure backend is running: `python app.py`
3. Verify HuggingFace token is valid
4. Check internet connection
5. Try a different YouTube video

**Want to customize?**

- See `README.md` for advanced configuration
- See `SETUP_GUIDE.md` for detailed setup

**Get HuggingFace Token:**

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it "YouTube RAG" (optional)
4. Make sure it's "Read" access (default)
5. Copy the token and paste in extension settings

---

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] `pip install -r requirements.txt` completed (in backend folder)
- [ ] `python app.py` running (terminal showing http://0.0.0.0:8000)
- [ ] Extension loaded in Chrome (chrome://extensions/)
- [ ] HuggingFace API token configured in extension settings
- [ ] Tested on a YouTube video with captions
- [ ] Asked a question and got an answer!

---

## 🎉 You're All Set!

Enjoy chatting with YouTube videos! Any questions? Check the full README.md or SETUP_GUIDE.md for more details.
