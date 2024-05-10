from yt_dlp import YoutubeDL

url = "https://www.youtube.com/watch?v=9bZkp7q19f0"

try:
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': 'test_clipwise_download.mp4',
        'quiet': False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print("✅ Downloaded:", info.get("title"))

except Exception as e:
    print("❌ Error:", e)
