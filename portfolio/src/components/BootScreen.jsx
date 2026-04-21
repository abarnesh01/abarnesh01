import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const BootScreen = ({ onComplete }) => {
    const [lines, setLines] = useState([]);
    const fullLines = [
        "Initializing system...",
        "Loading security modules...",
        "Establishing neural link...",
        "Bypassing firewall...",
        "Access granted.",
        "Welcome, Agent Abarnesh."
    ];

    useEffect(() => {
        let currentLine = 0;
        const interval = setInterval(() => {
            if (currentLine < fullLines.length) {
                setLines(prev => [...prev, fullLines[currentLine]]);
                currentLine++;
            } else {
                clearInterval(interval);
                setTimeout(() => onComplete(), 1000);
            }
        }, 400);

        return () => clearInterval(interval);
    }, [onComplete]);

    return (
        <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1 }}
            className="fixed inset-0 z-[9999] bg-[#050505] flex items-center justify-center p-6 font-mono"
        >
            <div className="max-w-md w-full">
                <div className="mb-4 flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="text-gray-500 text-xs ml-2">SYSTEM_BOOT_LOG</span>
                </div>

                <div className="space-y-2">
                    {lines.map((line, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className={`text-sm ${line.includes('granted') || line.includes('Welcome') ? 'text-[#00f5ff]' : 'text-gray-400'}`}
                        >
                            <span className="text-[#8a2be2] mr-2">❯</span>
                            {line}
                        </motion.div>
                    ))}
                    <motion.div
                        animate={{ opacity: [1, 0] }}
                        transition={{ repeat: Infinity, duration: 0.8 }}
                        className="w-2 h-5 bg-[#00f5ff] inline-block align-middle"
                    />
                </div>

                {/* Binary Rain Background Effect (Subtle) */}
                <div className="absolute inset-0 -z-10 opacity-[0.03] overflow-hidden pointer-events-none select-none text-[8px] leading-none text-[#00f5ff]">
                    {Array.from({ length: 50 }).map((_, i) => (
                        <div key={i} className="absolute whitespace-nowrap" style={{ left: `${i * 2}%`, top: '-20px', animation: `fall ${Math.random() * 10 + 5}s linear infinite`, animationDelay: `${Math.random() * 5}s` }}>
                            {Array.from({ length: 100 }).map(() => Math.round(Math.random())).join('\n')}
                        </div>
                    ))}
                </div>
            </div>

            <style jsx>{`
        @keyframes fall {
          to { transform: translateY(100vh); }
        }
      `}</style>
        </motion.div>
    );
};

export default BootScreen;
