// DOM Elements
const settingsBtn = document.getElementById("settingsBtn");
const settingsModal = document.getElementById("settingsModal");
const closeSettingsBtn = document.getElementById("closeSettingsBtn");
const saveSettingsBtn = document.getElementById("saveSettingsBtn");
const closeBtn = document.querySelector(".close-btn");
const apiTokenInput = document.getElementById("apiToken");
const backendUrlInput = document.getElementById("backendUrl");
const videoInfo = document.getElementById("videoInfo");
const statusMessage = document.getElementById("statusMessage");
const errorMessage = document.getElementById("errorMessage");
const chatContainer = document.getElementById("chatContainer");
const chatMessages = document.getElementById("chatMessages");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");
const setupMessage = document.getElementById("setupMessage");
const videoIdDisplay = document.getElementById("videoIdDisplay");

let currentVideoId = null;
let currentVideoTranscript = null;

// Initialize
document.addEventListener("DOMContentLoaded", async () => {
  await loadSettings();
  await getCurrentVideoId();
  attachEventListeners();
});

// Event Listeners
function attachEventListeners() {
  settingsBtn.addEventListener("click", openSettings);
  closeSettingsBtn.addEventListener("click", closeSettings);
  closeBtn.addEventListener("click", closeSettings);
  saveSettingsBtn.addEventListener("click", saveSettings);
  sendBtn.addEventListener("click", sendMessage);
  questionInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  // Close modal when clicking outside
  settingsModal.addEventListener("click", (e) => {
    if (e.target === settingsModal) closeSettings();
  });
}

// Settings Management
function openSettings() {
  settingsModal.classList.remove("hidden");
}

function closeSettings() {
  settingsModal.classList.add("hidden");
}

async function loadSettings() {
  const settings = await chrome.storage.sync.get(["apiToken", "backendUrl"]);
  if (settings.apiToken) {
    apiTokenInput.value = settings.apiToken;
  }
  if (settings.backendUrl) {
    backendUrlInput.value = settings.backendUrl;
  }
}

async function saveSettings() {
  const apiToken = apiTokenInput.value.trim();
  const backendUrl = backendUrlInput.value.trim();

  if (!apiToken) {
    alert("Please enter your HuggingFace API token");
    return;
  }

  if (!backendUrl) {
    alert("Please enter a backend URL");
    return;
  }

  await chrome.storage.sync.set({
    apiToken: apiToken,
    backendUrl: backendUrl,
  });

  closeSettings();
  showMessage("Settings saved! ✓", "success");

  // Reload to process video if available
  setTimeout(() => {
    window.location.reload();
  }, 500);
}

// Video Detection
async function getCurrentVideoId() {
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const tab = tabs[0];

    // Extract video ID from YouTube URL
    const url = tab.url;
    const videoIdMatch = url.match(
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    );

    if (videoIdMatch && videoIdMatch[1]) {
      currentVideoId = videoIdMatch[1];
      videoIdDisplay.textContent = currentVideoId;
      videoInfo.classList.remove("hidden");
      setupMessage.classList.add("hidden");

      // Check if backend is configured
      const settings = await chrome.storage.sync.get([
        "apiToken",
        "backendUrl",
      ]);
      if (settings.apiToken && settings.backendUrl) {
        await loadTranscript();
      } else {
        showError(
          "Please configure settings first (API token and backend URL required)",
        );
        setupMessage.classList.remove("hidden");
      }
    } else {
      showError("Please open a YouTube video page");
      videoInfo.classList.add("hidden");
    }
  } catch (error) {
    console.error("Error getting video ID:", error);
    showError("Error detecting video");
  }
}

// Transcript Loading
async function loadTranscript() {
  if (!currentVideoId) return;

  statusMessage.textContent = "Loading transcript...";

  try {
    const settings = await chrome.storage.sync.get(["backendUrl", "apiToken"]);
    const backendUrl = settings.backendUrl || "http://localhost:8000";

    const response = await fetch(`${backendUrl}/api/load-transcript`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        video_id: currentVideoId,
        api_token: settings.apiToken,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.statusText}`);
    }

    const data = await response.json();
    currentVideoTranscript = data.transcript;

    statusMessage.textContent = `✓ Transcript loaded (${Math.round(data.transcript.length / 1000)}k characters)`;
    chatContainer.classList.remove("hidden");
    chatMessages.innerHTML = "";
    addMessage("Ready to answer questions about this video! 🎬", "bot");
  } catch (error) {
    console.error("Error loading transcript:", error);
    showError(`Failed to load transcript: ${error.message}`);
    statusMessage.textContent = "❌ Failed to load transcript";
  }
}

// Chat Functionality
async function sendMessage() {
  const question = questionInput.value.trim();
  if (!question) return;

  if (!currentVideoTranscript) {
    showError("Transcript not loaded yet");
    return;
  }

  // Add user message
  addMessage(question, "user");
  questionInput.value = "";
  sendBtn.disabled = true;
  questionInput.disabled = true;

  // Show loading message
  addMessage("Thinking...", "loading");

  try {
    const settings = await chrome.storage.sync.get(["backendUrl", "apiToken"]);
    const backendUrl = settings.backendUrl || "http://localhost:8000";

    const response = await fetch(`${backendUrl}/api/ask-question`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        video_id: currentVideoId,
        question: question,
        api_token: settings.apiToken,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.statusText}`);
    }

    const data = await response.json();

    // Remove loading message and add response
    const loadingMsg = chatMessages.querySelector(".message.loading");
    if (loadingMsg) loadingMsg.remove();

    addMessage(data.answer, "bot");
  } catch (error) {
    console.error("Error sending message:", error);

    // Remove loading message
    const loadingMsg = chatMessages.querySelector(".message.loading");
    if (loadingMsg) loadingMsg.remove();

    addMessage(`Error: ${error.message}`, "bot");
  } finally {
    sendBtn.disabled = false;
    questionInput.disabled = false;
    questionInput.focus();
  }
}

function addMessage(text, sender) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${sender}`;
  messageDiv.textContent = text;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.remove("hidden");
}

function showMessage(message, type) {
  // You could enhance this for better feedback
  console.log(`[${type}] ${message}`);
}
