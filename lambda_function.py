import os
import logging
import json

from transcript_service import TranscriptService
from ml_tagger_service import MLTaggerService
from clipper_service import ClipperService
from storage_service import StorageService
from metadata_service import MetadataService
from dotenv import load_dotenv



# Set up logging
load_dotenv()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services (reuse across invocations if possible)
transcript_service = TranscriptService()
ml_tagger_service = MLTaggerService()
clipper_service = ClipperService()
storage_service = StorageService()
metadata_service = MetadataService()


def lambda_handler(event, context=None):
    """
    AWS Lambda entrypoint for ClipWise video clipping pipeline.
    Expects event['youtube_url'] as input.
    Returns signed URLs and metadata for generated clips.
    """
    try:
        youtube_url = event.get('youtube_url')
        if not youtube_url:
            logger.error("No YouTube URL provided in event.")
            return {"statusCode": 400, "body": json.dumps({"error": "Missing youtube_url in event."})}

        logger.info(f"Processing YouTube URL: {youtube_url}")

        # 1. Fetch transcript
        transcript_data = transcript_service.get_transcript(youtube_url)
        logger.info(f"Fetched transcript for video {transcript_data['video_id']} with {transcript_data['total_segments']} segments.")

        # 2. Find interesting segments
        clip_suggestions = ml_tagger_service.get_clip_suggestions(transcript_data)
        if not clip_suggestions:
            logger.warning("No interesting segments found.")
            return {"statusCode": 200, "body": json.dumps({"message": "No interesting segments found."})}
        logger.info(f"Found {len(clip_suggestions)} interesting segments.")

        # 3. Download and clip video
        clips = clipper_service.download_and_clip(youtube_url, clip_suggestions)
        if not clips:
            logger.error("No clips were created.")
            return {"statusCode": 500, "body": json.dumps({"error": "No clips were created."})}
        logger.info(f"Created {len(clips)} clips.")

        # 4. Upload clips to S3
        uploaded_clips = storage_service.upload_clips(clips)
        if not uploaded_clips:
            logger.error("No clips were uploaded to S3.")
            return {"statusCode": 500, "body": json.dumps({"error": "No clips were uploaded to S3."})}
        logger.info(f"Uploaded {len(uploaded_clips)} clips to S3.")

        # 5. Store metadata in DynamoDB
        stored_clips = metadata_service.store_clip_metadata(uploaded_clips)
        logger.info(f"Stored metadata for {len(stored_clips)} clips.")

        # 6. Prepare response
        response = {
            "video_id": transcript_data['video_id'],
            "clips": [
                {
                    "clip_id": clip['clip_id'],
                    "s3_url": clip['s3_url'],
                    "start_time": clip['start_time'],
                    "end_time": clip['end_time'],
                    "duration": clip['duration'],
                    "interest_score": clip['interest_score'],
                    "interest_reasons": clip['interest_reasons'],
                    "transcript_text": clip['transcript_text'],
                    "file_size_formatted": clip.get('file_size_formatted', ''),
                    "resolution": clip.get('resolution', ''),
                    "expires_at": clip.get('expires_at', None)
                }
                for clip in stored_clips
            ]
        }
        logger.info(f"Returning {len(response['clips'])} clips.")
        return {"statusCode": 200, "body": json.dumps(response)}

    except Exception as e:
        logger.exception(f"Unhandled error in lambda_handler: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})} 