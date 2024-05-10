import re
from datetime import datetime, timedelta
from typing import Dict, Any, List


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_timestamp(timestamp_str: str) -> float:
    """Convert HH:MM:SS format to seconds."""
    parts = timestamp_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    else:
        return float(parts[0])


def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {youtube_url}")


def validate_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL."""
    youtube_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=',
        r'https?://youtu\.be/',
        r'https?://(?:www\.)?youtube\.com/embed/'
    ]
    
    return any(re.match(pattern, url) for pattern in youtube_patterns)


def generate_clip_id(video_id: str, start_time: float, end_time: float) -> str:
    """Generate a unique clip ID based on video ID and timestamps."""
    start_str = str(int(start_time)).zfill(6)
    end_str = str(int(end_time)).zfill(6)
    return f"{video_id}_{start_str}_{end_str}"


def calculate_clip_duration(start_time: float, end_time: float) -> float:
    """Calculate the duration of a clip in seconds."""
    return end_time - start_time


def is_valid_clip_duration(start_time: float, end_time: float, max_duration: float = 30.0) -> bool:
    """Check if clip duration is within acceptable limits."""
    duration = calculate_clip_duration(start_time, end_time)
    return 0 < duration <= max_duration


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def get_expiry_timestamp(hours: int = 24) -> int:
    """Get Unix timestamp for expiry (default 24 hours from now)."""
    expiry_time = datetime.utcnow() + timedelta(hours=hours)
    return int(expiry_time.timestamp())


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename.strip() 