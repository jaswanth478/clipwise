import os
import boto3
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from utils import calculate_clip_duration, is_valid_clip_duration

logger = logging.getLogger(__name__)


class MLTaggerService:
    """Service for using AWS Comprehend to find interesting segments in transcripts."""

    def __init__(self):
        """Initialize AWS Comprehend client."""
        self.comprehend = boto3.client('comprehend', region_name='us-east-1')

        self.max_clip_duration = 30.0  # seconds
        self.min_clip_duration = 7.0   # slightly longer minimum clips
        self.max_clips_per_video = 10

        # Strong indicator words
        self.interesting_keywords = [
            'question', 'why', 'how', 'what', 'when', 'where', 'who',
            'important', 'key', 'crucial', 'essential', 'critical',
            'amazing', 'unbelievable', 'wow', 'problem', 'solution',
            'challenge', 'breakthrough', 'secret', 'reveal', 'discover',
            'find', 'found', 'best', 'worst', 'top', 'never', 'always',
            'exclusive', 'special', 'unique', 'trick', 'tip', 'hack'
        ]

        # Music-related tags that indicate non-speech (low interest)
        self.music_keywords = ['lyrics', 'instrumental', 'music', 'song', 'chorus', 'verse', 'beat']

    def get_clip_suggestions(self, transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        interesting_segments = self.find_interesting_segments(transcript_data)

        clip_suggestions = []
        for segment in interesting_segments:
            clip_suggestion = {
                'clip_id': f"{transcript_data['video_id']}_{int(segment['clip_start'])}_{int(segment['clip_end'])}",
                'video_id': transcript_data['video_id'],
                'start_time': segment['clip_start'],
                'end_time': segment['clip_end'],
                'duration': calculate_clip_duration(segment['clip_start'], segment['clip_end']),
                'interest_score': segment['interest_score'],
                'interest_reasons': segment['interest_reasons'],
                'transcript_text': segment['text'],
                'word_count': segment['word_count'],
                'char_count': segment['char_count']
            }
            clip_suggestions.append(clip_suggestion)

        return clip_suggestions

    def find_interesting_segments(self, transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            segments = transcript_data['transcript']
            video_id = transcript_data['video_id']

            logger.info(f"Analyzing transcript for video {video_id} with {len(segments)} segments")
            full_text = ' '.join([seg['text'] for seg in segments])

            sentiment = self._analyze_sentiment(full_text)
            key_phrases = self._extract_key_phrases(full_text)

            candidates = self._identify_interesting_segments(segments, sentiment, key_phrases)
            filtered = self._filter_and_rank_segments(candidates)

            logger.info(f"Selected {len(filtered)} interesting segments")
            return filtered

        except Exception as e:
            logger.error(f"Error finding interesting segments: {e}")
            raise

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        try:
            chunks = self._split_text_into_chunks(text, 4000)
            sentiments = [
                self.comprehend.detect_sentiment(Text=chunk, LanguageCode='en')
                for chunk in chunks
            ]
            return self._aggregate_sentiment_results(sentiments)
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return {'Sentiment': 'NEUTRAL', 'SentimentScore': {'Positive': 0.25, 'Negative': 0.25, 'Neutral': 0.5, 'Mixed': 0.0}}

    def _extract_key_phrases(self, text: str) -> List[str]:
        try:
            chunks = self._split_text_into_chunks(text, 4000)
            all_phrases = []
            for chunk in chunks:
                response = self.comprehend.detect_key_phrases(Text=chunk, LanguageCode='en')
                phrases = [phrase['Text'] for phrase in response['KeyPhrases']]
                all_phrases.extend(phrases)
            return all_phrases
        except Exception as e:
            logger.warning(f"Key phrase extraction failed: {e}")
            return []

    def _split_text_into_chunks(self, text: str, max_chars: int) -> List[str]:
        chunks, current = [], ""
        for sentence in text.split('.'):
            if len(current) + len(sentence) < max_chars:
                current += sentence + '.'
            else:
                if current: chunks.append(current.strip())
                current = sentence + '.'
        if current: chunks.append(current.strip())
        return chunks

    def _aggregate_sentiment_results(self, sentiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not sentiments:
            return {'Sentiment': 'NEUTRAL', 'SentimentScore': {'Positive': 0.25, 'Negative': 0.25, 'Neutral': 0.5, 'Mixed': 0.0}}

        avg = {'Positive': 0, 'Negative': 0, 'Neutral': 0, 'Mixed': 0}
        for s in sentiments:
            for k in avg:
                avg[k] += s['SentimentScore'].get(k, 0)
        total = len(sentiments)
        for k in avg:
            avg[k] /= total
        top_sentiment = max(avg, key=avg.get)
        return {'Sentiment': top_sentiment, 'SentimentScore': avg}

    def _identify_interesting_segments(self, segments: List[Dict[str, Any]], sentiment: Dict[str, Any], key_phrases: List[str]) -> List[Dict[str, Any]]:
        results = []
        for i, seg in enumerate(segments):
            score, reasons = 0, []
            text_lower = seg['text'].lower()

            if self._contains_question(text_lower):
                score += 3
                reasons.append('question')

            kw_count = self._count_keywords(text_lower, self.interesting_keywords)
            if kw_count:
                score += kw_count * 2
                reasons.append(f'{kw_count} keywords')

            phrase_count = self._count_phrase_matches(text_lower, key_phrases)
            if phrase_count:
                score += phrase_count
                reasons.append(f'{phrase_count} phrases')

            if sentiment['SentimentScore']['Positive'] > 0.6 or sentiment['SentimentScore']['Negative'] > 0.6:
                score += 2
                reasons.append('emotional')

            if seg['word_count'] > 20:
                score += 1
                reasons.append('enough content')

            if self._count_keywords(text_lower, self.music_keywords) > 3:
                reasons.append('music content')
                continue  # Skip music-heavy segments

            if i < 3 or i > len(segments) - 3:
                score += 1
                reasons.append('early/late')

            if score:
                results.append({
                    **seg,
                    'interest_score': score,
                    'interest_reasons': reasons,
                    'clip_start': seg['start'],
                    'clip_end': min(seg['end'], seg['start']) + self.max_clip_duration
                })
        return results

    def _contains_question(self, text: str) -> bool:
        return any(q in text for q in ['?', 'why', 'how', 'what', 'when', 'where', 'who'])

    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        return sum(1 for kw in keywords if kw in text)

    def _count_phrase_matches(self, text: str, phrases: List[str]) -> int:
        return sum(1 for phrase in phrases if phrase.lower() in text)

    def _filter_and_rank_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid = [s for s in segments if is_valid_clip_duration(s['clip_start'], s['clip_end'], self.max_clip_duration)]
        valid.sort(key=lambda s: s['interest_score'], reverse=True)
        return valid[:self.max_clips_per_video]
