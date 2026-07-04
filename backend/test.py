from youtube_transcript_api import YouTubeTranscriptApi

video_id = "UUheH1seQuE"   # Replace with your video ID

try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print("Success!")
    print(transcript[:5])

except Exception as e:
    print(type(e))
    print(e)