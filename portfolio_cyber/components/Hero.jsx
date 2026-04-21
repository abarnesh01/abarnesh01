'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, useState, useEffect } from 'react'
import SplineScene from './SplineScene'
import Image from 'next/image'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
      delayChildren: 0.3,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] },
  },
}

export default function Hero() {
  const containerRef = useRef(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const { scrollY } = useScroll()

  const y1 = useTransform(scrollY, [0, 500], [0, 200])
  const opacity = useTransform(scrollY, [0, 300], [1, 0])

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!containerRef.current) return
      const { clientX, clientY } = e
      setMousePos({ x: clientX, y: clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <section
      ref={containerRef}
      className="relative min-h-screen flex items-center overflow-hidden bg-dark-bg pt-20"
    >
      {/* Dynamic Cursor Spotlight */}
      <motion.div
        className="pointer-events-none fixed inset-0 z-30"
        animate={{
          background: `radial-gradient(600px circle at ${mousePos.x}px ${mousePos.y}px, rgba(0, 245, 255, 0.08), transparent 80%)`,
        }}
      />

      {/* Hero Background Gradient */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-transparent via-dark-bg/50 to-dark-bg" />
        <div className="absolute bottom-0 right-0 w-[800px] h-[800px] bg-neon-purple/5 rounded-full blur-[150px] translate-x-1/3 translate-y-1/3" />
      </div>

      <div className="container mx-auto px-6 relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* LEFT CONTENT */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-10"
        >
          {/* Profile Badge with Floating Animation and Tilt */}
          <motion.div
            variants={itemVariants}
            className="flex items-center gap-6"
          >
            <motion.div
              style={{ transformStyle: "preserve-3d" }}
              whileHover={{ rotateX: -10, rotateY: 10, scale: 1.05 }}
              animate={{ y: [0, -10, 0] }}
              transition={{
                y: { duration: 4, repeat: Infinity, ease: "easeInOut" },
                rotateX: { type: "spring", stiffness: 100 },
                rotateY: { type: "spring", stiffness: 100 }
              }}
              className="relative w-32 h-32 md:w-40 md:h-40 group cursor-pointer"
            >
              <div className="absolute inset-0 rounded-full bg-neon-cyan/20 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative w-full h-full rounded-full p-1 bg-gradient-neon shadow-[0_0_20px_rgba(0,245,255,0.2)]">
                <div className="w-full h-full rounded-full overflow-hidden bg-dark-bg border border-white/10">
                  <Image
                    src="/profile.png"
                    alt="Abarnesh S"
                    fill
                    className="object-cover transition-all duration-500 group-hover:scale-110"
                  />
                </div>
              </div>
              <div className="absolute -inset-4 rounded-full border border-neon-cyan/20 animate-spin-slow opacity-50 group-hover:opacity-100 transition-opacity" />
            </motion.div>

            <div className="space-y-1">
              <motion.div
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="text-neon-cyan text-[10px] font-bold tracking-[0.5em] uppercase mb-2"
              >
                Neural Link: Established
              </motion.div>
              <motion.h1
                variants={itemVariants}
                className="text-5xl md:text-8xl font-black tracking-tighter text-white uppercase italic"
              >
                Abarnesh <span className="text-neon-cyan neon-text tracking-normal not-italic">S</span>
              </motion.h1>
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="space-y-6">
            <h2 className="text-2xl md:text-3xl font-medium text-gray-300">
              Cybersecurity Engineer <span className="text-neon-red">_</span>
            </h2>
            <p className="text-lg text-gray-400 max-w-lg leading-relaxed font-light">
              Designing robust digital fortresses. Specializing in threat intelligence,
              automated defense systems, and securing the next generation of AI infrastructures.
            </p>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            variants={itemVariants}
            className="flex flex-wrap gap-6 mt-4"
          >
            <button className="glass-card px-8 py-4 text-white font-bold tracking-wide hover:shadow-[0_0_20px_rgba(0,245,255,0.4)] transition-all">
              Initiate Contact
            </button>
            <button className="px-8 py-4 border border-white/10 text-gray-400 font-medium rounded-xl hover:text-white hover:bg-white/5 transition-all">
              View Database
            </button>
          </motion.div>

          {/* Live Signal */}
          <motion.div
            variants={itemVariants}
            className="flex items-center gap-3 pt-4"
          >
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-neon-red opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-neon-red"></span>
            </span>
            <span className="text-xs text-gray-500 uppercase tracking-widest font-bold">System Status: Optimal</span>
          </motion.div>
        </motion.div>

        {/* RIGHT CONTENT: SPLINE */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          className="relative h-[500px] lg:h-[700px] w-full"
        >
          <div className="absolute inset-0 z-0">
            <SplineScene
              scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
              className="w-full h-full"
            />
          </div>

          {/* Neon Grid Overlay */}
          <div className="absolute inset-0 pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay" />
        </motion.div>
      </div>

      {/* Scroll Down Indicator */}
      <motion.div
        style={{ opacity }}
        className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3 z-20"
      >
        <span className="text-[10px] text-gray-500 uppercase tracking-[0.4em] font-bold">Protocol: Scroll</span>
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-px h-16 bg-gradient-to-b from-neon-cyan to-transparent"
        />
      </motion.div>
    </section>
  )
}
