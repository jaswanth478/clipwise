import os
from typing import List, Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
import logging

from utils import extract_video_id, validate_youtube_url

logger = logging.getLogger(__name__)


class TranscriptService:
    """Service for fetching and processing YouTube video transcripts."""
    
    def __init__(self):
        self.formatter = JSONFormatter()
    
    def get_transcript(self, youtube_url: str, languages: List[str] = None) -> Dict[str, Any]:
        """
        Fetch transcript for a YouTube video.
        
        Args:
            youtube_url: YouTube video URL
            languages: List of language codes to try (default: ['en', 'en-US'])
            
        Returns:
            Dict containing transcript data and metadata
        """
        if not validate_youtube_url(youtube_url):
            raise ValueError(f"Invalid YouTube URL: {youtube_url}")
        
        if languages is None:
            languages = ['en', 'en-US']
        
        try:
            video_id = extract_video_id(youtube_url)
            logger.info(f"Fetching transcript for video ID: {video_id}")
            
            # Try to get transcript in preferred languages
            transcript = None
            used_language = None
            
            for lang in languages:
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                    transcript = transcript_list
                    used_language = lang
                    break
                except Exception as e:
                    logger.warning(f"Failed to get transcript in {lang}: {e}")
                    continue
            
            if transcript is None:
                # Try to get transcript in any available language
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    transcript = transcript_list
                    used_language = "auto"
                except Exception as e:
                    raise Exception(f"Could not fetch transcript for video {video_id}: {e}")
            
            # Process transcript data
            processed_transcript = self._process_transcript(transcript)
            
            return {
                'video_id': video_id,
                'youtube_url': youtube_url,
                'language': used_language,
                'transcript': processed_transcript,
                'total_segments': len(processed_transcript),
                'total_duration': processed_transcript[-1]['end'] if processed_transcript else 0
            }
            
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            raise
    
    def _process_transcript(self, transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process raw transcript data into a more usable format.
        
        Args:
            transcript: Raw transcript from YouTube API
            
        Returns:
            Processed transcript with additional metadata
        """
        processed = []
        
        for i, segment in enumerate(transcript):
            processed_segment = {
                'index': i,
                'start': segment['start'],
                'end': segment['start'] + segment['duration'],
                'duration': segment['duration'],
                'text': segment['text'].strip(),
                'word_count': len(segment['text'].split()),
                'char_count': len(segment['text'])
            }
            processed.append(processed_segment)
        
        return processed
    
    def get_transcript_text(self, youtube_url: str) -> str:
        """
        Get full transcript text as a single string.
        
        Args:
            youtube_url: YouTube video URL
            
        Returns:
            Full transcript text
        """
        transcript_data = self.get_transcript(youtube_url)
        return ' '.join([segment['text'] for segment in transcript_data['transcript']])
    
    def get_transcript_segments(self, youtube_url: str, 
                               min_duration: float = 0.0,
                               max_duration: float = float('inf')) -> List[Dict[str, Any]]:
        """
        Get transcript segments filtered by duration.
        
        Args:
            youtube_url: YouTube video URL
            min_duration: Minimum segment duration in seconds
            max_duration: Maximum segment duration in seconds
            
        Returns:
            Filtered transcript segments
        """
        transcript_data = self.get_transcript(youtube_url)
        
        filtered_segments = [
            segment for segment in transcript_data['transcript']
            if min_duration <= segment['duration'] <= max_duration
        ]
        
        return filtered_segments
    
    def export_transcript_json(self, youtube_url: str) -> str:
        """
        Export transcript as formatted JSON string.
        
        Args:
            youtube_url: YouTube video URL
            
        Returns:
            Formatted JSON string
        """
        transcript_data = self.get_transcript(youtube_url)
        return self.formatter.format_transcript(transcript_data['transcript'])
    
    def get_video_metadata(self, youtube_url: str) -> Dict[str, Any]:
        """
        Get basic video metadata (requires YouTube API key for full metadata).
        
        Args:
            youtube_url: YouTube video URL
            
        Returns:
            Basic video metadata
        """
        video_id = extract_video_id(youtube_url)
        
        # For now, return basic info available from transcript
        # In v2, this could be enhanced with YouTube Data API
        transcript_data = self.get_transcript(youtube_url)
        
        return {
            'video_id': video_id,
            'youtube_url': youtube_url,
            'duration': transcript_data['total_duration'],
            'segment_count': transcript_data['total_segments'],
            'language': transcript_data['language']
        } 