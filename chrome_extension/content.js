// Content script for YouTube pages
// This script runs in the context of YouTube and can access page content

console.log("YouTube Transcript RAG Content Script Loaded");

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getVideoInfo") {
    // Extract video ID from the page
    const videoId = getVideoIdFromPage();
    sendResponse({ videoId: videoId });
  }
});

function getVideoIdFromPage() {
  // Method 1: From URL
  const url = window.location.href;
  const match = url.match(/v=([a-zA-Z0-9_-]{11})/);
  if (match) return match[1];

  // Method 2: From meta tag
  const metaTag = document.querySelector('meta[property="og:url"]');
  if (metaTag) {
    const metaMatch = metaTag.content.match(/v=([a-zA-Z0-9_-]{11})/);
    if (metaMatch) return metaMatch[1];
  }

  return null;
}
