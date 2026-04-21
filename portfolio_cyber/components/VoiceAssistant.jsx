'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

export default function VoiceAssistant() {
    const [isSupported, setIsSupported] = useState(false)
    const [isSpeaking, setIsSpeaking] = useState(false)

    useEffect(() => {
        if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
            setIsSupported(true)
        }
    }, [])

    const speak = (text) => {
        if (!isSupported) return
        window.speechSynthesis.cancel()
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.pitch = 1
        utterance.rate = 1
        utterance.volume = 0.8
        utterance.onstart = () => setIsSpeaking(true)
        utterance.onend = () => setIsSpeaking(false)
        window.speechSynthesis.speak(utterance)
    }

    const welcome = () => {
        speak("System Uplink Established. Welcome to Abarnesh's Neural Portfolio. Cybersecurity modules are active and ready for your command.")
    }

    return (
        <div className="fixed top-24 right-10 z-40">
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={welcome}
                className="glass-card px-4 py-2 border-neon-red/30 flex items-center gap-3 group"
            >
                <div className={`w-2 h-2 rounded-full ${isSpeaking ? 'bg-neon-red animate-ping' : 'bg-gray-600'}`} />
                <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-400 group-hover:text-neon-red transition-colors">
                    Initialize Audio Uplink
                </span>
                <span className="text-xs">🎙️</span>
            </motion.button>
        </div>
    )
}
