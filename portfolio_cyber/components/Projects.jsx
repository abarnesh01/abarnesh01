'use client'

import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { useRef } from 'react'

const projects = [
  {
    title: 'PII MASKING ENGINE',
    description: 'Autonomous OCR system for redacting sensitive data from secure documents with military-grade precision.',
    tech: ['Python', 'EasyOCR', 'OpenCV'],
    color: 'from-[#00f5ff]/20 to-[#8a2be2]/20',
    accent: '#00f5ff',
    features: ['PII Detection', 'Deep Redaction', 'Batch Engine'],
  },
  {
    title: 'CIVIC AI SHIELD',
    description: 'Real-time threat detection network utilizing neural CCTV analysis for proactive public safety.',
    tech: ['Neural Networks', 'Computer Vision', 'React'],
    color: 'from-[#ff0040]/20 to-[#8a2be2]/20',
    accent: '#ff0040',
    features: ['Vision Analysis', 'Threat Ranking', 'Neural Alerts'],
  },
  {
    title: 'SOC CYBER-CORE',
    description: 'High-performance SOC dashboard with ML-driven anomaly detection for critical network nodes.',
    tech: ['Node.js', 'React', 'Sklearn AI'],
    color: 'from-[#8a2be2]/20 to-[#00f5ff]/20',
    accent: '#8a2be2',
    features: ['Flow Tracking', 'Neural Anomaly', 'Live Uplink'],
  },
]

function ProjectCard({ project, idx }) {
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const mouseXSpring = useSpring(x)
  const mouseYSpring = useSpring(y)

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["10deg", "-10deg"])
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-10deg", "10deg"])

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const width = rect.width
    const height = rect.height
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top
    const xPct = mouseX / width - 0.5
    const yPct = mouseY / height - 0.5
    x.set(xPct)
    y.set(yPct)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
  }

  return (
    <motion.div
      style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: idx * 0.15, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="group relative h-[500px] w-full"
    >
      <div
        className="absolute inset-x-4 inset-y-4 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-2xl z-0"
        style={{ backgroundColor: `${project.accent}20` }}
      />

      <div className="relative h-full w-full glass-card p-8 flex flex-col justify-between border-white/5 group-hover:border-neon-cyan/50 transition-all duration-500">
        <div style={{ transform: "translateZ(50px)" }} className="space-y-6">
          <div className={`h-1 w-12 rounded-full`} style={{ backgroundColor: project.accent }} />
          <h3 className="text-3xl font-bold text-white tracking-tighter leading-tight uppercase underline-offset-8 group-hover:underline">
            {project.title}
          </h3>
          <p className="text-gray-400 font-light text-lg leading-relaxed">
            {project.description}
          </p>

          <div className="flex flex-wrap gap-2">
            {project.features.map((f, i) => (
              <span key={i} className="text-[10px] font-bold tracking-[0.2em] px-3 py-1 bg-white/5 border border-white/10 text-gray-400 uppercase">
                {f}
              </span>
            ))}
          </div>
        </div>

        <div style={{ transform: "translateZ(30px)" }} className="pt-6 border-t border-white/5">
          <div className="flex items-center justify-between">
            <div className="flex gap-4">
              {project.tech.map((t, i) => (
                <span key={i} className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">{t}</span>
              ))}
            </div>
            <motion.button
              whileHover={{ x: 5 }}
              className="text-neon-cyan text-sm font-bold uppercase tracking-widest flex items-center gap-2"
            >
              Access →
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default function Projects() {
  return (
    <section id="projects" className="min-h-screen flex items-center justify-center bg-dark-bg py-24 relative overflow-hidden">
      <div className="container mx-auto px-6 relative z-10 w-full">
        <div className="flex flex-col items-center mb-20 text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-4 tracking-tighter">
            PROTOTYPE <span className="text-neon-cyan neon-text">CHAMBER</span>
          </h2>
          <p className="text-gray-500 uppercase tracking-[0.3em] text-sm">Deployment Log</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 max-w-7xl mx-auto">
          {projects.map((project, idx) => (
            <ProjectCard key={idx} project={project} idx={idx} />
          ))}
        </div>
      </div>
    </section>
  )
}
