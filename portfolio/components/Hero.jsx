'use client'

import { motion } from 'framer-motion'
import { useRef } from 'react'

const textVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.8,
      ease: 'easeOut',
    },
  }),
}

export default function Hero() {
  const mouseX = useRef(0)
  const mouseY = useRef(0)

  const handleMouseMove = (e) => {
    mouseX.current = e.clientX
    mouseY.current = e.clientY
  }

  return (
    <section
      onMouseMove={handleMouseMove}
      className="relative min-h-screen flex items-center justify-center bg-gradient-dark overflow-hidden"
    >
      {/* Animated background gradient */}
      <motion.div
        className="absolute inset-0 opacity-30"
        animate={{
          background: [
            'radial-gradient(circle at 20% 50%, #00f5ff 0%, transparent 50%)',
            'radial-gradient(circle at 80% 50%, #8a2be2 0%, transparent 50%)',
            'radial-gradient(circle at 20% 50%, #00f5ff 0%, transparent 50%)',
          ],
        }}
        transition={{ duration: 10, repeat: Infinity }}
      />

      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        {/* Main heading */}
        <motion.h1
          className="text-7xl md:text-8xl font-bold mb-6 neon-text"
          custom={0}
          variants={textVariants}
          initial="hidden"
          animate="visible"
        >
          ABARNESH S
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          className="text-xl md:text-2xl mb-4 text-neon-cyan"
          custom={1}
          variants={textVariants}
          initial="hidden"
          animate="visible"
        >
          Cybersecurity Engineer • SOC Analyst • CTF Player
        </motion.p>

        {/* Description */}
        <motion.p
          className="text-lg md:text-xl mb-8 text-gray-300"
          custom={2}
          variants={textVariants}
          initial="hidden"
          animate="visible"
        >
          Elite security researcher specializing in threat detection, AI security,
          and SOC operations
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          className="flex gap-4 justify-center mb-12"
          custom={3}
          variants={textVariants}
          initial="hidden"
          animate="visible"
        >
          <button className="px-8 py-3 bg-neon-cyan text-black font-bold rounded hover-glow">
            View Work
          </button>
          <button className="px-8 py-3 border-2 border-neon-red text-neon-red font-bold rounded hover-glow">
            Contact
          </button>
        </motion.div>

        {/* Social Links */}
        <motion.div
          className="flex gap-6 justify-center text-2xl"
          custom={4}
          variants={textVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.a
            href="https://github.com/abarnesh"
            whileHover={{ scale: 1.2 }}
            className="text-neon-cyan hover:text-neon-red transition"
          >
            GitHub
          </motion.a>
          <motion.a
            href="https://linkedin.com/in/abarnesh"
            whileHover={{ scale: 1.2 }}
            className="text-neon-purple hover:text-neon-cyan transition"
          >
            LinkedIn
          </motion.a>
          <motion.a
            href="mailto:abarnesh772@gmail.com"
            whileHover={{ scale: 1.2 }}
            className="text-neon-red hover:text-neon-purple transition"
          >
            Email
          </motion.a>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="text-neon-cyan">↓</div>
      </motion.div>
    </section>
  )
}
