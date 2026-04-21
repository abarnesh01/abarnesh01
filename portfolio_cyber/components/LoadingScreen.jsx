'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'

export default function LoadingScreen({ onComplete }) {
    const [logs, setLogs] = useState([])
    const [complete, setComplete] = useState(false)

    const messages = [
        { text: "INITIALIZING SYSTEM...", delay: 500 },
        { text: "ESTABLISHING SECURE UPLINK...", delay: 800 },
        { text: "LOADING NEURAL MODULES...", delay: 600 },
        { text: "MOUNTING 3D INTERFACE...", delay: 700 },
        { text: "AUTHENTICATING BIO-METRICS...", delay: 900 },
        { text: "ACCESS GRANTED.", delay: 500, final: true },
    ]

    useEffect(() => {
        let current = 0
        let isActive = true

        const addLog = () => {
            if (!isActive) return
            if (current < messages.length) {
                setLogs(prev => [...prev, messages[current]])
                setTimeout(addLog, messages[current].delay)
                current++
            } else {
                setTimeout(() => {
                    if (isActive) setComplete(true)
                }, 1000)
                setTimeout(() => {
                    if (isActive) onComplete?.()
                }, 1500)
            }
        }
        addLog()
        return () => { isActive = false }
    }, [])

    return (
        <AnimatePresence>
            {!complete && (
                <motion.div
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[100] bg-dark-bg flex items-center justify-center font-mono p-6 overflow-hidden"
                >
                    {/* HUD Grid Background */}
                    <div className="absolute inset-0 opacity-20 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%] transition-opacity duration-300" />

                    <div className="max-w-md w-full space-y-4 relative">
                        <div className="text-neon-cyan/50 text-[10px] tracking-[0.5em] mb-8 animate-pulse uppercase">
                            Neural Link Establishment in progress...
                        </div>

                        <div className="space-y-2">
                            {logs.map((log, i) => {
                                if (!log) return null;
                                return (
                                    <motion.div
                                        key={i}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className={`text-sm ${log.final ? 'text-neon-cyan font-bold' : 'text-gray-500'}`}
                                    >
                                        <span className="mr-2">[{new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}]</span>
                                        {log.text}
                                    </motion.div>
                                );
                            })}
                        </div>

                        {/* Progress Bar */}
                        <div className="relative h-1 w-full bg-white/5 mt-8 overflow-hidden rounded-full">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: "100%" }}
                                transition={{ duration: 3.5, ease: "linear" }}
                                className="absolute top-0 left-0 h-full bg-neon-cyan shadow-[0_0_15px_rgba(0,245,255,0.8)]"
                            />
                        </div>

                        <div className="flex justify-between items-center text-[8px] text-gray-700 mt-2 uppercase tracking-widest">
                            <span>Kernel: Cyber_OS_v1.0</span>
                            <span>Status: Active</span>
                        </div>
                    </div>

                    <div className="absolute top-10 left-10 text-neon-cyan text-[8px] tracking-widest opacity-20 uppercase">
                        Sector 7G-1 // Monitoring Mode
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}
