# 🎬 ClipWise

ClipWise is an intelligent video clipping backend built for YouTube videos. It analyzes transcripts, detects viral-worthy moments, generates short clips, and stores them on AWS S3 with metadata in DynamoDB.

---

## ✅ Features (v1)

- Extracts YouTube transcripts
- Uses AWS Comprehend to detect **interesting segments** based on:
  - Keywords
  - Key phrases
  - Sentiment
  - Question detection
- Clips videos using `ffmpeg` and uploads to AWS S3
- Stores metadata in DynamoDB with TTL (for clip expiration)
- API-ready design (via `lambda_function.py`)
- Basic support for filtering music/non-speech content

---

## 🚧 Coming Soon

- 🎯 ML model trained on viral content patterns (YouTube Shorts, Podcasts, Music)
- 🌍 Multi-site video support (e.g., Vimeo, Twitter)
- 👥 User tiers (Free, Pro)
- 📈 Analytics dashboard
- 🧠 Improved segment ranking with NLP finetuned on real data

---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone this repo
cd clipwise


python3 -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows


pip install -r requirements.txt


AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
DYNAMODB_TABLE_NAME=your-dynamodb-table
CLIP_EXPIRY_HOURS=24



AWS Setup (Required)
NOTE: You must be logged into the AWS CLI with proper permissions.

✅ Create an S3 bucket to store clips

✅ Create a DynamoDB table (e.g., clipwise_metadata)

clip_id as Primary Key

Enable TTL on ttl field

✅ Ensure AWS CLI is configured (via aws configure or ~/.aws/credentials)

✅ You can test locally without deploying Lambda, thanks to modular code


🧪 Running Locally
python3 test.py


🧠 ML v2 (Coming)
We're building a better ML tagging service, trained on:

Real viral clips from YouTube Shorts, TikTok

Podcast highlight datasets

Segment match between full video + most-watched short

This will allow ClipWise to detect:

⚡ Punchlines

❓ Important questions

💬 Clickbait-worthy quotes

🧠 Trendy visual/audio segments (non-transcript based)

🙌 Contributing
This is currently a private PoC (proof of concept). If you're interested in contributing, reach out!