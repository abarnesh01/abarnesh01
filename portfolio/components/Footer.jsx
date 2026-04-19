'use client'

import { motion } from 'framer-motion'

export default function Footer() {
  return (
    <footer className="bg-dark-bg border-t border-neon-cyan border-opacity-20 py-8">
      <div className="max-w-6xl mx-auto px-4 text-center">
        <motion.p
          className="text-gray-400 mb-4"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          "Access granted. Monitoring continues..."
        </motion.p>

        <motion.p
          className="text-sm text-gray-500"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          © 2026 Abarnesh S. All rights reserved.
        </motion.p>
      </div>
    </footer>
  )
}
