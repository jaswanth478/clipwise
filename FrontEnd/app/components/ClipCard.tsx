'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
    Play,
    Clock,
    Download,
    Share2,
    Heart,
    Copy,
    Check,
    Loader2
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
    /* ──────────────────────────────────────── state ─────────────────────────────────────── */
    const [loading, setLoading] = useState(false)
    const [showPreview, setShowPreview] = useState(false)
    const [copied, setCopied] = useState(false)
    const [liked, setLiked] = useState(false)

    /* ───────────────────────────────────── helpers ─────────────────────────────────────── */
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

    /* ─────────────────────────────────── actions ───────────────────────────────────────── */
    const handleDownload = async () => {
        setLoading(true)
        try {
            const response = await fetch(clip.s3_url)
            const blob = await response.blob()
            const url = URL.createObjectURL(blob)
            const fileName = clip.s3_url.split('/').pop()?.split('?')[0] || 'clip.mp4'

            const a = document.createElement('a')
            a.href = url
            a.download = fileName
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)

            URL.revokeObjectURL(url)
        } catch (err) {
            console.error('Download failed:', err)
        } finally {
            setLoading(false)
        }
    }

    const handlePreview = () => setShowPreview(true)

    /* ───────────────────────────────────── JSX ─────────────────────────────────────────── */
    return (
        <>
            {/* ╭──────────────── loader overlay ───────────────╮ */}
            {loading && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="flex flex-col items-center">
                        <Loader2 className="w-10 h-10 animate-spin text-white" />
                        <p className="mt-2 text-2xl font-bold text-white">Downloading clip…</p>
                    </div>
                </div>
            )}

            {/* ╭──────────────── preview modal ────────────────╮ */}
            {showPreview && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black/90"
                    onClick={() => setShowPreview(false)} // close on background click
                >
                    {/* Stop propagation inside the video container to prevent accidental closing */}
                    <div
                        className="relative"
                        onClick={(e) => e.stopPropagation()} // prevents click inside video from closing
                    >
                        <button
                            tabIndex={0}
                            aria-label="Close preview"
                            onKeyDown={(e) => {
                                if (e.key === 'Escape') {
                                    e.preventDefault();
                                    setShowPreview(false);
                                }
                            }}
                            onClick={() => setShowPreview(false)}
                            className="absolute top-4 right-4 text-3xl font-bold text-white z-50"
                        >
                            ✕
                        </button>

                        <video
                            src={clip.s3_url}
                            controls
                            autoPlay
                            muted={false} // allow sound
                            className="w-full max-w-7xl h-auto rounded-lg shadow-2xl"
                            ref={(ref) => {
                                if (ref) ref.volume = 0.7; // set volume programmatically
                            }}
                        />
                    </div>
                </div>
            )}


            {/* ╭──────────────── card ─────────────────────────╮ */}
            <motion.div
                className="clip-card overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg"
                whileHover={{ y: -4 }}
                transition={{ duration: 0.2 }}
            >
                {/* thumbnail with play button */}
                <div className="relative aspect-video bg-gradient-to-br from-gray-100 to-gray-200">
                    <div className="absolute inset-0 flex items-center justify-center">
                        <motion.button
                            onClick={handlePreview}
                            className="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 shadow-lg transition-colors hover:bg-white"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <Play className="ml-1 h-6 w-6 text-primary-600" />
                        </motion.button>
                    </div>
                </div>

                {/* content */}
                <div className="p-6">
                    {/* transcript */}
                    <p className="mb-4 line-clamp-3 text-sm text-gray-700">
                        {clip.transcript_text}
                    </p>

                    {/* time range */}
                    <div className="mb-4 flex items-center text-sm text-gray-500">
                        <Clock className="mr-2 h-4 w-4" />
                        {formatTime(clip.start_time)} – {formatTime(clip.end_time)}
                    </div>

                    {/* interest reasons */}
                    {clip.interest_reasons.length > 0 && (
                        <div className="mb-4 flex flex-wrap gap-1">
                            {clip.interest_reasons.slice(0, 3).map((reason, idx) => (
                                <span
                                    key={idx}
                                    className="rounded-full bg-primary-100 px-2 py-1 text-xs text-primary-700"
                                >
                                    {reason}
                                </span>
                            ))}
                        </div>
                    )}

                    {/* file info */}
                    <div className="mb-4 flex items-center justify-between text-xs text-gray-500">
                        <span>{clip.file_size_formatted}</span>
                        <span>{clip.resolution}</span>
                    </div>

                    {/* actions */}
                    <div className="flex space-x-2">
                        <motion.button
                            onClick={handleDownload}
                            className="flex flex-1 items-center justify-center rounded-lg bg-primary-600 py-2 px-3 text-sm font-medium text-white transition-colors hover:bg-primary-700"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <Download className="mr-1 h-4 w-4" />
                            Download
                        </motion.button>

                        <motion.button
                            onClick={() => {
                                if (navigator.share) {
                                    navigator
                                        .share({
                                            title: 'Check out this clip!',
                                            text: 'Generated with ClipWise AI',
                                            url: clip.s3_url
                                        })
                                        .catch(console.error)
                                } else {
                                    copyUrl()
                                }
                            }}
                            className="flex flex-1 items-center justify-center rounded-lg bg-gray-100 py-2 px-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <Share2 className="mr-1 h-4 w-4" />
                            Share
                        </motion.button>

                        <motion.button
                            onClick={() => setLiked(!liked)}
                            className={`flex items-center justify-center rounded-lg p-2 transition-colors ${liked
                                ? 'bg-red-100 text-red-600'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                        >
                            <Heart className={`h-4 w-4 ${liked ? 'fill-current' : ''}`} />
                        </motion.button>
                    </div>

                    {/* copy url */}
                    <div className="mt-3">
                        <motion.button
                            onClick={copyUrl}
                            className="flex w-full items-center justify-center py-1 text-xs text-gray-500 transition-colors hover:text-gray-700"
                            whileHover={{ scale: 1.02 }}
                        >
                            {copied ? (
                                <>
                                    <Check className="mr-1 h-3 w-3 text-green-500" />
                                    URL Copied!
                                </>
                            ) : (
                                <>
                                    <Copy className="mr-1 h-3 w-3" />
                                    Copy URL
                                </>
                            )}
                        </motion.button>
                    </div>
                </div>
            </motion.div>
        </>
    )
}
