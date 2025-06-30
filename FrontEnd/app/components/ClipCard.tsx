'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
    Play,
    Clock,
    TrendingUp,
    Download,
    Share2,
    Heart,
    Copy,
    Check,
    ExternalLink
} from 'lucide-react'

interface Clip {
    clip_id: string
    s3_url: string
    start_time: number
    end_time: number
    duration: number
    interest_score: number
    interest_reasons: string[]
    transcript_text: string
    file_size_formatted: string
    resolution: string
    expires_at: string | null
}

interface ClipCardProps {
    clip: Clip
}

export default function ClipCard({ clip }: ClipCardProps) {
    const [copied, setCopied] = useState(false)
    const [liked, setLiked] = useState(false)

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = Math.floor(seconds % 60)
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const copyUrl = () => {
        navigator.clipboard.writeText(clip.s3_url)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const handleDownload = () => {
        // Open download in new tab
        window.open(clip.s3_url, '_blank')
    }

    const handleShare = async () => {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'Check out this clip!',
                    text: 'Generated with ClipWise AI',
                    url: clip.s3_url,
                })
            } catch (err) {
                console.error('Error sharing:', err)
            }
        } else {
            copyUrl()
        }
    }

    return (
        <motion.div
            className="clip-card bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200"
            whileHover={{ y: -4 }}
            transition={{ duration: 0.2 }}
        >
            {/* Video Preview */}
            <div className="relative aspect-video bg-gradient-to-br from-gray-100 to-gray-200">
                <div className="absolute inset-0 flex items-center justify-center">
                    <motion.button
                        onClick={() => window.open(clip.s3_url, '_blank')}
                        className="w-16 h-16 bg-white/90 rounded-full flex items-center justify-center shadow-lg hover:bg-white transition-colors"
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <Play className="w-6 h-6 text-primary-600 ml-1" />
                    </motion.button>
                </div>

                {/* Duration Badge */}
                <div className="absolute bottom-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-sm">
                    {formatTime(clip.duration)}
                </div>

                {/* Interest Score Badge */}
                <div className="absolute top-2 left-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-2 py-1 rounded-full text-xs font-semibold flex items-center">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {typeof clip.interest_score === 'number' ? Math.round(clip.interest_score * 100) : clip.interest_score}%
                </div>
            </div>

            {/* Content */}
            <div className="p-6">
                {/* Transcript */}
                <p className="text-gray-700 text-sm line-clamp-3 mb-4">
                    {clip.transcript_text}
                </p>

                {/* Time Range */}
                <div className="flex items-center text-sm text-gray-500 mb-4">
                    <Clock className="w-4 h-4 mr-2" />
                    {formatTime(clip.start_time)} - {formatTime(clip.end_time)}
                </div>

                {/* Interest Reasons */}
                {clip.interest_reasons.length > 0 && (
                    <div className="mb-4">
                        <div className="flex flex-wrap gap-1">
                            {clip.interest_reasons.slice(0, 3).map((reason, index) => (
                                <span
                                    key={index}
                                    className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full"
                                >
                                    {reason}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* File Info */}
                <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                    <span>{clip.file_size_formatted}</span>
                    <span>{clip.resolution}</span>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2">
                    <motion.button
                        onClick={handleDownload}
                        className="flex-1 bg-primary-600 text-white py-2 px-3 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center justify-center"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <Download className="w-4 h-4 mr-1" />
                        Download
                    </motion.button>

                    <motion.button
                        onClick={handleShare}
                        className="flex-1 bg-gray-100 text-gray-700 py-2 px-3 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors flex items-center justify-center"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <Share2 className="w-4 h-4 mr-1" />
                        Share
                    </motion.button>

                    <motion.button
                        onClick={() => setLiked(!liked)}
                        className={`p-2 rounded-lg transition-colors flex items-center justify-center ${liked
                            ? 'bg-red-100 text-red-600'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                    >
                        <Heart className={`w-4 h-4 ${liked ? 'fill-current' : ''}`} />
                    </motion.button>
                </div>

                {/* Copy URL Button */}
                <div className="mt-3">
                    <motion.button
                        onClick={copyUrl}
                        className="w-full text-xs text-gray-500 hover:text-gray-700 transition-colors flex items-center justify-center py-1"
                        whileHover={{ scale: 1.02 }}
                    >
                        {copied ? (
                            <>
                                <Check className="w-3 h-3 mr-1 text-green-500" />
                                URL Copied!
                            </>
                        ) : (
                            <>
                                <Copy className="w-3 h-3 mr-1" />
                                Copy URL
                            </>
                        )}
                    </motion.button>
                </div>
            </div>
        </motion.div>
    )
} 