// Service Worker for Chrome Extension

chrome.runtime.onInstalled.addListener(() => {
  console.log("YouTube Transcript RAG Extension Installed");
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "checkBackendHealth") {
    checkBackendHealth(request.backendUrl).then((isHealthy) => {
      sendResponse({ healthy: isHealthy });
    });
    return true; // Will respond asynchronously
  }
});

async function checkBackendHealth(backendUrl) {
  try {
    const response = await fetch(`${backendUrl}/health`, {
      method: "GET",
      timeout: 5000,
    });
    return response.ok;
  } catch (error) {
    console.error("Backend health check failed:", error);
    return false;
  }
}
