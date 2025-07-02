import os
import boto3
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError

from utils import format_file_size, sanitize_filename

logger = logging.getLogger(__name__)


class StorageService:
    """Service for uploading clips to S3 and generating signed URLs."""
    
    def __init__(self):
        """Initialize S3 client and configuration."""
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.environ.get('S3_BUCKET_NAME', 'clipwise-v1')
        
        # S3 configuration
        self.clip_prefix = 'clips/'
        self.preview_prefix = 'previews/'
        self.signed_url_expiry = 3600 * 24 * 5 # 30 days
        
        # Content type for video files
        self.video_content_type = 'video/mp4'
    
    def upload_clips(self, clips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Upload multiple clips to S3.
        
        Args:
            clips: List of clip data from ClipperService
            
        Returns:
            List of clips with S3 URLs and metadata
        """
        uploaded_clips = []
        
        for clip in clips:
            try:
                uploaded_clip = self._upload_single_clip(clip)
                if uploaded_clip:
                    uploaded_clips.append(uploaded_clip)
            except Exception as e:
                logger.error(f"Failed to upload clip {clip.get('clip_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully uploaded {len(uploaded_clips)} clips to S3")
        return uploaded_clips
    
    def _upload_single_clip(self, clip: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Upload a single clip to S3.
        
        Args:
            clip: Clip data with file path and metadata
            
        Returns:
            Clip data with S3 URL and upload metadata
        """
        try:
            clip_id = clip['clip_id']
            file_path = clip['file_path']
            filename = clip['filename']
            
            # Create S3 key
            s3_key = f"{self.clip_prefix}{clip_id}/{filename}"
            
            # Upload file to S3
            upload_result = self._upload_file_to_s3(file_path, s3_key)
            
            if not upload_result:
                return None
            
            # Generate signed URL
            signed_url = self._generate_signed_url(s3_key)
            
            # Prepare updated clip data
            uploaded_clip = {
                **clip,
                's3_key': s3_key,
                's3_url': signed_url,
                'upload_timestamp': datetime.utcnow().isoformat(),
                'file_size_formatted': format_file_size(clip.get('file_size', 0))
            }
            
            logger.info(f"Uploaded clip {clip_id} to S3: {s3_key}")
            return uploaded_clip
            
        except Exception as e:
            logger.error(f"Error uploading clip {clip.get('clip_id', 'unknown')}: {e}")
            return None
    
    def _upload_file_to_s3(self, file_path: str, s3_key: str) -> bool:
        """
        Upload a file to S3.
        
        Args:
            file_path: Local file path
            s3_key: S3 object key
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            # Upload file with metadata
            extra_args = {
                'ContentType': self.video_content_type,
                'Metadata': {
                    'uploaded-by': 'clipwise',
                    'upload-timestamp': datetime.utcnow().isoformat()
                }
            }
            
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            return True
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            return False
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return False
    
    def _generate_signed_url(self, s3_key: str, expiry_seconds: int = None) -> str:
        """
        Generate a signed URL for an S3 object.
        
        Args:
            s3_key: S3 object key
            expiry_seconds: URL expiry time in seconds
            
        Returns:
            Signed URL string
        """
        try:
            if expiry_seconds is None:
                expiry_seconds = self.signed_url_expiry
            
            # Generate presigned URL
            signed_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiry_seconds
            )
            
            return signed_url
            
        except Exception as e:
            logger.error(f"Error generating signed URL for {s3_key}: {e}")
            raise
    
    def upload_preview(self, preview_data: bytes, clip_id: str) -> Optional[str]:
        """
        Upload a clip preview to S3.
        
        Args:
            preview_data: Preview video data as bytes
            clip_id: Clip ID for naming
            
        Returns:
            S3 key of uploaded preview or None
        """
        try:
            # Create S3 key for preview
            preview_filename = f"preview_{clip_id}.mp4"
            s3_key = f"{self.preview_prefix}{clip_id}/{preview_filename}"
            
            # Upload preview data
            extra_args = {
                'ContentType': self.video_content_type,
                'Metadata': {
                    'uploaded-by': 'clipwise',
                    'type': 'preview',
                    'upload-timestamp': datetime.utcnow().isoformat()
                }
            }
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=preview_data,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Uploaded preview for clip {clip_id}: {s3_key}")
            return s3_key
            
        except Exception as e:
            logger.error(f"Error uploading preview for clip {clip_id}: {e}")
            return None
    
    def delete_clip(self, clip_id: str) -> bool:
        """
        Delete a clip and its preview from S3.
        
        Args:
            clip_id: Clip ID to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # List objects with clip_id prefix
            clip_prefix = f"{self.clip_prefix}{clip_id}/"
            preview_prefix = f"{self.preview_prefix}{clip_id}/"
            
            objects_to_delete = []
            
            # Find clip objects
            try:
                clip_objects = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=clip_prefix
                )
                if 'Contents' in clip_objects:
                    objects_to_delete.extend([obj['Key'] for obj in clip_objects['Contents']])
            except Exception as e:
                logger.warning(f"Error listing clip objects: {e}")
            
            # Find preview objects
            try:
                preview_objects = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=preview_prefix
                )
                if 'Contents' in preview_objects:
                    objects_to_delete.extend([obj['Key'] for obj in preview_objects['Contents']])
            except Exception as e:
                logger.warning(f"Error listing preview objects: {e}")
            
            # Delete objects
            if objects_to_delete:
                delete_response = self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={
                        'Objects': [{'Key': key} for key in objects_to_delete],
                        'Quiet': True
                    }
                )
                
                deleted_count = len(delete_response.get('Deleted', []))
                logger.info(f"Deleted {deleted_count} objects for clip {clip_id}")
                return True
            else:
                logger.warning(f"No objects found to delete for clip {clip_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting clip {clip_id}: {e}")
            return False
    
    def get_clip_url(self, clip_id: str, filename: str = None) -> Optional[str]:
        """
        Get a signed URL for a specific clip.
        
        Args:
            clip_id: Clip ID
            filename: Optional specific filename
            
        Returns:
            Signed URL or None
        """
        try:
            if filename:
                s3_key = f"{self.clip_prefix}{clip_id}/{filename}"
            else:
                # Try to find the main clip file
                s3_key = f"{self.clip_prefix}{clip_id}/{clip_id}.mp4"
            
            return self._generate_signed_url(s3_key)
            
        except Exception as e:
            logger.error(f"Error getting URL for clip {clip_id}: {e}")
            return None
    
    def check_bucket_exists(self) -> bool:
        """
        Check if the configured S3 bucket exists.
        
        Returns:
            True if bucket exists, False otherwise
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"S3 bucket {self.bucket_name} does not exist")
                return False
            else:
                logger.error(f"Error checking bucket {self.bucket_name}: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error checking bucket: {e}")
            return False
    
    def get_bucket_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the S3 bucket.
        
        Returns:
            Dictionary with bucket statistics
        """
        try:
            stats = {
                'bucket_name': self.bucket_name,
                'total_objects': 0,
                'total_size': 0,
                'clips_count': 0,
                'previews_count': 0
            }
            
            # List all objects
            paginator = self.s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket_name):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        stats['total_objects'] += 1
                        stats['total_size'] += obj['Size']
                        
                        key = obj['Key']
                        if key.startswith(self.clip_prefix):
                            stats['clips_count'] += 1
                        elif key.startswith(self.preview_prefix):
                            stats['previews_count'] += 1
            
            # Format sizes
            stats['total_size_formatted'] = format_file_size(stats['total_size'])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting bucket stats: {e}")
            return {'error': str(e)} 