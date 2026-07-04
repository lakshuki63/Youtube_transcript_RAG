import requests

video_id = "UUheH1seQuE"      # Your video ID

url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en"

r = requests.get(url)

print("Status:", r.status_code)
print("Content-Type:", r.headers.get("content-type"))
print("Length:", len(r.text))
print("Response:")
print(r.text[:500])