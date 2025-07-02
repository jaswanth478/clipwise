import os
import tempfile
import io
from typing import List, Dict, Any, Optional, Tuple
import logging
import ffmpeg
import requests
import yt_dlp

from utils import format_timestamp, sanitize_filename, is_valid_clip_duration

logger = logging.getLogger(__name__)


class ClipperService:
    """Service for downloading and clipping YouTube videos using yt_dlp and ffmpeg."""

    def __init__(self):
        """Initialize the clipper service."""
        self.temp_dir = tempfile.mkdtemp()
        self.max_clip_duration = 30.0  # seconds
        self.min_clip_duration = 5.0   # seconds

    def download_and_clip(self, youtube_url: str, clip_suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Starting download and clip process for {len(clip_suggestions)} clips")

            video_path, video_id = self._download_video(youtube_url)

            clips = []
            for suggestion in clip_suggestions:
                try:
                    suggestion['video_id'] = video_id
                    clip_data = self._create_clip(video_path, suggestion)
                    if clip_data:
                        clips.append(clip_data)
                except Exception as e:
                    logger.error(f"Failed to create clip for {suggestion['clip_id']}: {e}")
                    continue

            self._cleanup_file(video_path)

            logger.info(f"Successfully created {len(clips)} clips")
            return clips

        except Exception as e:
            logger.error(f"Error in download_and_clip: {e}")
            raise

    def _download_video(self, youtube_url: str) -> Tuple[str, str]:
        try:
            logger.info(f"Downloading video: {youtube_url}")

            temp_file = os.path.join(self.temp_dir, "downloaded_video.mp4")

            ydl_opts = {
                'format': 'bestvideo[height<=720]+bestaudio/best/worst',
                'outtmpl': temp_file,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                video_title = info.get("title", "unknown")
                video_id = info.get("id", "unknown")
                duration = info.get("duration", 0)

            logger.info(f"Video title: {video_title}")
            logger.info(f"Video duration: {duration} seconds")
            logger.info(f"Video downloaded to: {temp_file}")
            return temp_file, video_id

        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            # Try to get more information about available formats
            try:
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    formats = info.get('formats', [])
                    logger.error(f"Available formats: {[f.get('format_id', 'unknown') for f in formats[:5]]}")
            except Exception as format_error:
                logger.error(f"Could not get format info: {format_error}")
            raise

    def _create_clip(self, video_path: str, suggestion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            start_time = suggestion['start_time']
            end_time = suggestion['end_time']
            clip_id = suggestion['clip_id']

            if not is_valid_clip_duration(start_time, end_time, self.max_clip_duration):
                logger.warning(f"Clip duration invalid for {clip_id}: {end_time - start_time}s")
                return None

            output_filename = f"{clip_id}.mp4"
            output_path = os.path.join(self.temp_dir, output_filename)

            self._extract_clip_ffmpeg(video_path, output_path, start_time, end_time)

            clip_metadata = self._get_clip_metadata(output_path)

            clip_data = {
                'clip_id': clip_id,
                'video_id': suggestion['video_id'],
                'file_path': output_path,
                'filename': output_filename,
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'file_size': clip_metadata.get('file_size', 0),
                'resolution': clip_metadata.get('resolution', 'unknown'),
                'interest_score': suggestion['interest_score'],
                'interest_reasons': suggestion['interest_reasons'],
                'transcript_text': suggestion['transcript_text'],
                'word_count': suggestion['word_count'],
                'char_count': suggestion['char_count']
            }

            logger.info(f"Created clip: {clip_id} ({clip_data['duration']:.1f}s)")
            return clip_data

        except Exception as e:
            logger.error(f"Error creating clip {suggestion.get('clip_id', 'unknown')}: {e}")
            return None

    def _extract_clip_ffmpeg(self, input_path: str, output_path: str, start_time: float, end_time: float):
        try:
            duration = end_time - start_time
            stream = ffmpeg.input(input_path, ss=start_time, t=duration)
            output = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                acodec='aac',
                video_bitrate='1000k',
                audio_bitrate='128k',
                preset='fast',
                movflags='faststart'
            )
            ffmpeg.run(output, overwrite_output=True, quiet=True)
        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            raise

    def _get_clip_metadata(self, clip_path: str) -> Dict[str, Any]:
        try:
            metadata = {}
            if os.path.exists(clip_path):
                metadata['file_size'] = os.path.getsize(clip_path)

            probe = ffmpeg.probe(clip_path)
            if probe and 'streams' in probe:
                video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
                if video_stream:
                    metadata['resolution'] = f"{video_stream.get('width', 'unknown')}x{video_stream.get('height', 'unknown')}"
                    metadata['duration'] = float(video_stream.get('duration', 0))

            return metadata
        except Exception as e:
            logger.warning(f"Error getting clip metadata: {e}")
            return {'file_size': 0, 'resolution': 'unknown'}

    def _cleanup_file(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Error cleaning up file {file_path}: {e}")

    def cleanup_temp_files(self):
        try:
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                self._cleanup_file(file_path)
            if os.path.exists(self.temp_dir):
                os.rmdir(self.temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")

    def get_clip_preview(self, clip_path: str, preview_duration: float = 5.0) -> Optional[bytes]:
        try:
            preview_filename = f"preview_{os.path.basename(clip_path)}"
            preview_path = os.path.join(self.temp_dir, preview_filename)

            stream = ffmpeg.input(clip_path, t=preview_duration)
            output = ffmpeg.output(
                stream,
                preview_path,
                vcodec='libx264',
                acodec='aac',
                video_bitrate='500k',
                audio_bitrate='64k',
                preset='ultrafast'
            )

            ffmpeg.run(output, overwrite_output=True, quiet=True)

            with open(preview_path, 'rb') as f:
                preview_data = f.read()

            self._cleanup_file(preview_path)

            return preview_data
        except Exception as e:
            logger.error(f"Error creating clip preview: {e}")
            return None
