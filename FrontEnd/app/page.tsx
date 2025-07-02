'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Play,
    Scissors,
    Sparkles,
    Copy,
    Check,
    ExternalLink,
    Clock,
    TrendingUp,
    Zap,
    Star,
    Video,
    Download,
    Share2,
    Heart
} from 'lucide-react'
import ClipCard from './components/ClipCard'
import UrlInput from './components/UrlInput'
import V2Features from './components/V2Features'

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

interface ApiResponse {
    video_id: string
    clips: Clip[]
}

export default function Home() {
    const [url, setUrl] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [clips, setClips] = useState<Clip[]>([])
    const [error, setError] = useState('')
    const [videoId, setVideoId] = useState('')
    const [debugData, setDebugData] = useState<any>(null)

    const handleSubmit = async (youtubeUrl: string) => {
        setIsLoading(true)
        setError('')
        setClips([])
        setVideoId('')

        try {
            const response = await fetch('http://127.0.0.1:5000/clip', {

                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ youtube_url: youtubeUrl }),
            })

            if (!response.ok) {
                throw new Error('Failed to process video')
            }

            const responseData = await response.json()

            // Handle the nested response structure
            let data: ApiResponse
            if (responseData.body) {
                // If response has a body property, parse it
                data = JSON.parse(responseData.body)
            } else {
                // Direct response
                data = responseData
            }

            console.log('API Response:', data) // Debug log
            console.log('Clips:', data.clips) // Debug log
            console.log('Video ID:', data.video_id) // Debug log
            setClips(data.clips || [])
            setVideoId(data.video_id || '')

            // dont'show s3_url in debug data
            const sanitizedClips = data.clips.map((clip: Clip) => ({
                ...clip,
                s3_url: undefined, // Remove s3_url for security
            }))
            setDebugData(sanitizedClips) // Store for debugging
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen">
            {/* Header */}
            <header className="relative overflow-hidden bg-gradient-to-r from-primary-600 to-primary-800 text-white">
                <div className="absolute inset-0 bg-black/20"></div>
                <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="text-center"
                    >
                        <div className="flex items-center justify-center mb-6">
                            <div className="p-3 bg-white/20 rounded-full mr-4">
                                <Scissors className="w-8 h-8" />
                            </div>
                            <h1 className="text-4xl md:text-6xl font-bold">ClipWise</h1>
                        </div>
                        <p className="text-xl md:text-2xl text-primary-100 mb-8">
                            AI-Powered Video Clipping Made Simple
                        </p>
                        <div className="flex items-center justify-center space-x-4 text-sm text-primary-200">
                            <div className="flex items-center">
                                <Sparkles className="w-4 h-4 mr-2" />
                                AI-Powered
                            </div>
                            <div className="flex items-center">
                                <Zap className="w-4 h-4 mr-2" />
                                Lightning Fast
                            </div>
                            <div className="flex items-center">
                                <Star className="w-4 h-4 mr-2" />
                                High Quality
                            </div>
                        </div>
                    </motion.div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                {/* URL Input Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="mb-16"
                >
                    <UrlInput onSubmit={handleSubmit} isLoading={isLoading} />
                </motion.div>

                {/* Loading State */}
                <AnimatePresence>
                    {isLoading && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="text-center py-16"
                        >
                            <div className="inline-flex items-center space-x-3 bg-white rounded-full px-6 py-4 shadow-lg">
                                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                                <span className="text-lg font-medium text-gray-700">
                                    Processing your video
                                </span>
                                <span className="loading-dots"></span>
                            </div>
                            <p className="mt-4 text-gray-500">
                                Our AI is analyzing the content and creating engaging clips...
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Error State */}
                <AnimatePresence>
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="mb-8 bg-red-50 border border-red-200 rounded-lg p-6"
                        >
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                                        <span className="text-red-600 font-bold">!</span>
                                    </div>
                                </div>
                                <div className="ml-3">
                                    <h3 className="text-sm font-medium text-red-800">
                                        Error processing video
                                    </h3>
                                    <p className="mt-1 text-sm text-red-700">{error}</p>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Results Section */}
                <AnimatePresence>
                    {clips?.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6 }}
                            className="mb-16"
                        >
                            <div className="text-center mb-8">
                                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                                    Your AI-Generated Clips
                                </h2>
                                <p className="text-gray-600">
                                    {clips.length} engaging clip{clips.length !== 1 ? 's' : ''} ready to share
                                    {debugData?.from_cache && (
                                        <span className="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                            <span className="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                                            From Cache
                                        </span>
                                    )}
                                </p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {clips.map((clip, index) => (
                                    <motion.div
                                        key={clip.clip_id}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.6, delay: index * 0.1 }}
                                    >
                                        <ClipCard clip={clip} />
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Debug Section */}
                {debugData && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-6"
                    >
                        <h3 className="text-lg font-semibold text-blue-800 mb-2">Debug Info</h3>
                        <pre className="text-xs text-blue-700 overflow-auto">
                            {JSON.stringify(debugData, null, 2)}
                        </pre>
                    </motion.div>
                )}

                {/* V2 Features Preview */}
                <V2Features />
            </main>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center">
                        <div className="flex items-center justify-center mb-4">
                            <Scissors className="w-6 h-6 mr-2" />
                            <span className="text-xl font-bold">ClipWise</span>
                        </div>
                        <p className="text-gray-400">
                            Transform your videos into engaging content with AI
                        </p>
                        <div className="mt-6 flex justify-center space-x-6 text-sm text-gray-400">
                            <span>© 2025 ClipWise</span>
                            <span>•</span>
                            <span>Privacy Policy</span>
                            <span>•</span>
                            <span>Terms of Service</span>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
} 