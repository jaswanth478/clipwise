'use client'

import { motion } from 'framer-motion'
import {
    Sparkles,
    Users,
    Zap,
    Palette,
    Globe,
    BarChart3,
    Music,
    Smartphone,
    Cloud,
    Shield
} from 'lucide-react'

const features = [
    {
        icon: Users,
        title: 'Team Collaboration',
        description: 'Share clips with your team and collaborate on content creation',
        color: 'from-blue-500 to-blue-600'
    },
    {
        icon: Palette,
        title: 'Custom Branding',
        description: 'Add your logo, colors, and custom overlays to clips',
        color: 'from-purple-500 to-purple-600'
    },
    {
        icon: Music,
        title: 'Background Music',
        description: 'Add royalty-free music tracks to enhance your clips',
        color: 'from-green-500 to-green-600'
    },
    {
        icon: Smartphone,
        title: 'Mobile App',
        description: 'Create clips on the go with our mobile application',
        color: 'from-orange-500 to-orange-600'
    },
    {
        icon: Globe,
        title: 'Multi-Platform',
        description: 'Support for TikTok, Instagram, Twitter, and more',
        color: 'from-pink-500 to-pink-600'
    },
    {
        icon: BarChart3,
        title: 'Analytics Dashboard',
        description: 'Track performance and engagement of your clips',
        color: 'from-indigo-500 to-indigo-600'
    },
    {
        icon: Cloud,
        title: 'Cloud Storage',
        description: 'Store and organize your clips in the cloud',
        color: 'from-cyan-500 to-cyan-600'
    },
    {
        icon: Shield,
        title: 'Advanced Security',
        description: 'Enterprise-grade security and privacy controls',
        color: 'from-red-500 to-red-600'
    }
]

export default function V2Features() {
    return (
        <section className="py-16">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                viewport={{ once: true }}
                className="text-center mb-12"
            >
                <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-full text-sm font-semibold mb-4">
                    <Sparkles className="w-4 h-4 mr-2" />
                    Coming Soon - V2
                </div>
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                    The Future of Video Clipping
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                    We're building the ultimate platform for content creators.
                    Here's what's coming in ClipWise V2.
                </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {features.map((feature, index) => (
                    <motion.div
                        key={feature.title}
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: index * 0.1 }}
                        viewport={{ once: true }}
                        className="group"
                    >
                        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300 h-full">
                            <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${feature.color} text-white mb-4 group-hover:scale-110 transition-transform duration-300`}>
                                <feature.icon className="w-6 h-6" />
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600 text-sm leading-relaxed">
                                {feature.description}
                            </p>
                        </div>
                    </motion.div>
                ))}
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.8 }}
                viewport={{ once: true }}
                className="text-center mt-12"
            >
                <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-8 text-white">
                    <Zap className="w-12 h-12 mx-auto mb-4 text-yellow-300" />
                    <h3 className="text-2xl font-bold mb-2">Get Early Access</h3>
                    <p className="text-primary-100 mb-6">
                        Be the first to experience the next generation of video clipping
                    </p>
                    <button className="bg-white text-primary-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                        Join Waitlist
                    </button>
                </div>
            </motion.div>
        </section>
    )
} 