'use client'

import { motion } from 'framer-motion'

export default function Footer() {
  return (
    <footer className="bg-dark-bg border-t border-white/5 py-12 relative overflow-hidden">
      <div className="absolute inset-0 bg-neon-cyan/5 opacity-20 pointer-events-none" />

      <div className="container mx-auto px-6 relative z-10 text-center space-y-6">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          className="flex flex-col items-center gap-4"
        >
          <div className="h-[1px] w-12 bg-neon-cyan/50" />
          <p className="text-gray-500 font-bold uppercase tracking-[0.5em] text-[10px]">
            Connection Terminated // Monitoring Mode Active
          </p>
          <div className="h-[1px] w-12 bg-neon-cyan/50" />
        </motion.div>

        <motion.p
          className="text-gray-400 font-light tracking-wide text-sm"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
        >
          © 2026 <span className="text-white font-bold">ABARNESH S</span>. Engineered for Resilience.
        </motion.p>
      </div>
    </footer>
  )
}
