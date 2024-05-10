import os
import boto3
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from decimal import Decimal

from utils import get_expiry_timestamp

logger = logging.getLogger(__name__)


class MetadataService:
    """Service for storing and retrieving clip metadata in DynamoDB."""
    
    def __init__(self):
        """Initialize DynamoDB client and configuration."""
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('DYNAMO_TABLE_NAME', 'ClipMeta')
        self.table = self.dynamodb.Table(self.table_name)
        
        # TTL configuration (1 day expiry for normal users)
        self.default_ttl_hours = 24
        
        # Ensure table exists
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Ensure the DynamoDB table exists, create if it doesn't."""
        try:
            # Try to describe the table
            self.table.load()
            logger.info(f"DynamoDB table {self.table_name} exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating DynamoDB table {self.table_name}")
                self._create_table()
            else:
                logger.error(f"Error checking table {self.table_name}: {e}")
                raise
    
    def _create_table(self):
        """Create the DynamoDB table with proper schema."""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'clip_id',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'video_id',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'clip_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'video_id',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'ttl'
                }
            )
            
            # Wait for table to be created
            table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
            logger.info(f"Created DynamoDB table {self.table_name}")
            
        except Exception as e:
            logger.error(f"Error creating table {self.table_name}: {e}")
            raise
    
    def store_clip_metadata(self, clips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Store metadata for multiple clips in DynamoDB.
        
        Args:
            clips: List of clip data from StorageService
            
        Returns:
            List of clips with stored metadata confirmation
        """
        stored_clips = []
        
        for clip in clips:
            try:
                stored_clip = self._store_single_clip_metadata(clip)
                if stored_clip:
                    stored_clips.append(stored_clip)
            except Exception as e:
                logger.error(f"Failed to store metadata for clip {clip.get('clip_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully stored metadata for {len(stored_clips)} clips")
        return stored_clips
    
    def _store_single_clip_metadata(self, clip: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Store metadata for a single clip in DynamoDB.

        Args:
            clip: Clip data with metadata

        Returns:
            Clip data with storage confirmation
        """
        try:
            clip_id = clip['clip_id']
            video_id = clip['video_id']

            # Convert float values to Decimal for DynamoDB
            def to_dynamo_safe(value):
                if isinstance(value, float):
                    return Decimal(str(value))
                elif isinstance(value, dict):
                    return {k: to_dynamo_safe(v) for k, v in value.items()}
                elif isinstance(value, list):
                    return [to_dynamo_safe(v) for v in value]
                else:
                    return value

            # Prepare item
            item = to_dynamo_safe({
                'clip_id': clip_id,
                'video_id': video_id,
                's3_key': clip.get('s3_key', ''),
                's3_url': clip.get('s3_url', ''),
                'start_time': clip.get('start_time', 0),
                'end_time': clip.get('end_time', 0),
                'duration': clip.get('duration', 0),
                'file_size': clip.get('file_size', 0),
                'file_size_formatted': clip.get('file_size_formatted', ''),
                'resolution': clip.get('resolution', 'unknown'),
                'interest_score': clip.get('interest_score', 0),
                'interest_reasons': clip.get('interest_reasons', []),
                'transcript_text': clip.get('transcript_text', ''),
                'word_count': clip.get('word_count', 0),
                'char_count': clip.get('char_count', 0),
                'upload_timestamp': clip.get('upload_timestamp', datetime.utcnow().isoformat()),
                'created_at': datetime.utcnow().isoformat(),
                'ttl': get_expiry_timestamp(self.default_ttl_hours)
            })

            self.table.put_item(Item=item)

            stored_clip = {
                **clip,
                'metadata_stored': True,
                'storage_timestamp': datetime.utcnow().isoformat(),
                'expires_at': datetime.fromtimestamp(item['ttl']).isoformat()
            }

            logger.info(f"Stored metadata for clip {clip_id}")
            return stored_clip

        except Exception as e:
            logger.error(f"Error storing metadata for clip {clip.get('clip_id', 'unknown')}: {e}")
            return None

    def get_clip_metadata(self, clip_id: str, video_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a specific clip.
        
        Args:
            clip_id: Clip ID
            video_id: Optional video ID for composite key
            
        Returns:
            Clip metadata or None
        """
        try:
            if video_id:
                response = self.table.get_item(
                    Key={
                        'clip_id': clip_id,
                        'video_id': video_id
                    }
                )
            else:
                # Query by clip_id only
                response = self.table.query(
                    KeyConditionExpression='clip_id = :clip_id',
                    ExpressionAttributeValues={
                        ':clip_id': clip_id
                    }
                )
            
            if 'Item' in response:
                return response['Item']
            elif 'Items' in response and response['Items']:
                return response['Items'][0]  # Return first match
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving metadata for clip {clip_id}: {e}")
            return None
    
    def get_clips_by_video(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get all clips for a specific video.
        
        Args:
            video_id: Video ID
            
        Returns:
            List of clip metadata
        """
        try:
            response = self.table.query(
                IndexName='video_id-index',  # Requires GSI
                KeyConditionExpression='video_id = :video_id',
                ExpressionAttributeValues={
                    ':video_id': video_id
                }
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error retrieving clips for video {video_id}: {e}")
            return []
    
    def update_clip_metadata(self, clip_id: str, video_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update metadata for a specific clip.
        
        Args:
            clip_id: Clip ID
            video_id: Video ID
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for key, value in updates.items():
                attr_name = f"#{key}"
                attr_value = f":{key}"
                
                update_expression += f"{attr_name} = {attr_value}, "
                expression_attribute_names[attr_name] = key
                expression_attribute_values[attr_value] = value
            
            # Add updated timestamp
            update_expression += "#updated_at = :updated_at"
            expression_attribute_names["#updated_at"] = "updated_at"
            expression_attribute_values[":updated_at"] = datetime.utcnow().isoformat()
            
            # Remove trailing comma
            update_expression = update_expression.rstrip(", ")
            
            # Update item
            self.table.update_item(
                Key={
                    'clip_id': clip_id,
                    'video_id': video_id
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )
            
            logger.info(f"Updated metadata for clip {clip_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metadata for clip {clip_id}: {e}")
            return False
    
    def delete_clip_metadata(self, clip_id: str, video_id: str) -> bool:
        """
        Delete metadata for a specific clip.
        
        Args:
            clip_id: Clip ID
            video_id: Video ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            self.table.delete_item(
                Key={
                    'clip_id': clip_id,
                    'video_id': video_id
                }
            )
            
            logger.info(f"Deleted metadata for clip {clip_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting metadata for clip {clip_id}: {e}")
            return False
    
    def extend_clip_ttl(self, clip_id: str, video_id: str, hours: int = 24) -> bool:
        """
        Extend the TTL for a clip.
        
        Args:
            clip_id: Clip ID
            video_id: Video ID
            hours: Number of hours to extend TTL
            
        Returns:
            True if extension successful, False otherwise
        """
        try:
            new_ttl = get_expiry_timestamp(hours)
            
            self.table.update_item(
                Key={
                    'clip_id': clip_id,
                    'video_id': video_id
                },
                UpdateExpression='SET ttl = :ttl',
                ExpressionAttributeValues={
                    ':ttl': new_ttl
                }
            )
            
            logger.info(f"Extended TTL for clip {clip_id} by {hours} hours")
            return True
            
        except Exception as e:
            logger.error(f"Error extending TTL for clip {clip_id}: {e}")
            return False
    
    def get_expiring_clips(self, hours: int = 1) -> List[Dict[str, Any]]:
        """
        Get clips that will expire within the specified hours.
        
        Args:
            hours: Number of hours to look ahead
            
        Returns:
            List of clips expiring soon
        """
        try:
            current_time = int(datetime.utcnow().timestamp())
            expiry_threshold = current_time + (hours * 3600)
            
            # Scan table for expiring clips
            response = self.table.scan(
                FilterExpression='ttl <= :expiry_threshold',
                ExpressionAttributeValues={
                    ':expiry_threshold': expiry_threshold
                }
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error getting expiring clips: {e}")
            return []
    
    def get_table_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the DynamoDB table.
        
        Returns:
            Dictionary with table statistics
        """
        try:
            response = self.table.meta.client.describe_table(TableName=self.table_name)
            
            stats = {
                'table_name': self.table_name,
                'item_count': response['Table'].get('ItemCount', 0),
                'table_size_bytes': response['Table'].get('TableSizeBytes', 0),
                'table_status': response['Table'].get('TableStatus', 'unknown'),
                'billing_mode': response['Table'].get('BillingModeSummary', {}).get('BillingMode', 'unknown')
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting table stats: {e}")
            return {'error': str(e)} 