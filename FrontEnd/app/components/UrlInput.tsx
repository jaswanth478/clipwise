'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, Copy, Check, ExternalLink } from 'lucide-react'

interface UrlInputProps {
    onSubmit: (url: string) => void
    isLoading: boolean
}

export default function UrlInput({ onSubmit, isLoading }: UrlInputProps) {
    const [url, setUrl] = useState('')
    const [copied, setCopied] = useState(false)

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (url.trim() && !isLoading) {
            onSubmit(url.trim())
        }
    }

    const handlePaste = async () => {
        try {
            const text = await navigator.clipboard.readText()
            setUrl(text)
        } catch (err) {
            console.error('Failed to read clipboard:', err)
        }
    }

    const copyUrl = () => {
        navigator.clipboard.writeText(url)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const isValidYoutubeUrl = (url: string) => {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/
        return youtubeRegex.test(url)
    }

    return (
        <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                    Transform Any YouTube Video
                </h2>
                <p className="text-lg text-gray-600">
                    Paste a YouTube URL and let our AI create engaging clips for you
                </p>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200"
            >
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-700 mb-2">
                            YouTube URL
                        </label>
                        <div className="relative">
                            <input
                                id="youtube-url"
                                type="url"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="https://www.youtube.com/watch?v=..."
                                className={`w-full px-4 py-4 pr-12 border rounded-xl text-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${url && !isValidYoutubeUrl(url) ? 'border-red-300 bg-red-50' : 'border-gray-300'
                                    }`}
                                disabled={isLoading}
                            />
                            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex space-x-2">
                                {url && (
                                    <button
                                        type="button"
                                        onClick={copyUrl}
                                        className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                                        title="Copy URL"
                                    >
                                        {copied ? <Check className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
                                    </button>
                                )}
                                <button
                                    type="button"
                                    onClick={handlePaste}
                                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                                    title="Paste from clipboard"
                                >
                                    <ExternalLink className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                        {url && !isValidYoutubeUrl(url) && (
                            <p className="mt-2 text-sm text-red-600">
                                Please enter a valid YouTube URL
                            </p>
                        )}
                    </div>

                    <motion.button
                        type="submit"
                        disabled={!url.trim() || !isValidYoutubeUrl(url) || isLoading}
                        className={`w-full py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-200 flex items-center justify-center space-x-2 ${!url.trim() || !isValidYoutubeUrl(url) || isLoading
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-gradient-to-r from-primary-600 to-primary-700 text-white hover:from-primary-700 hover:to-primary-800 transform hover:scale-105 shadow-lg'
                            }`}
                        whileHover={!isLoading ? { scale: 1.02 } : {}}
                        whileTap={!isLoading ? { scale: 0.98 } : {}}
                    >
                        {isLoading ? (
                            <>
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                <span>Processing...</span>
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5" />
                                <span>Generate Clips</span>
                            </>
                        )}
                    </motion.button>
                </form>

                <div className="mt-6 pt-6 border-t border-gray-200">
                    <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
                        <div className="flex items-center">
                            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                            Free to use
                        </div>
                        <div className="flex items-center">
                            <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                            AI-powered
                        </div>
                        <div className="flex items-center">
                            <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                            High quality
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    )
} 