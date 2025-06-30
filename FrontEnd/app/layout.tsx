import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'ClipWise - AI-Powered Video Clipping',
    description: 'Transform YouTube videos into engaging clips with AI',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
                    {children}
                </div>
            </body>
        </html>
    )
} 