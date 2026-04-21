'use client'

import { motion } from 'framer-motion'

export default function About() {
  return (
    <section id="about" className="min-h-screen flex items-center justify-center bg-dark-bg py-24 relative">
      <div className="absolute top-1/2 left-0 w-96 h-96 bg-neon-cyan/5 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2" />

      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="max-w-4xl mx-auto"
        >
          <div className="flex flex-col items-center mb-16 text-center">
            <motion.span
              initial={{ scaleX: 0 }}
              whileInView={{ scaleX: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="h-px w-24 bg-neon-cyan mb-8 origin-center"
            />
            <h2 className="text-4xl md:text-6xl font-bold mb-4 tracking-tighter">
              THE <span className="text-neon-cyan neon-text">ARCHITECT</span>
            </h2>
            <p className="text-gray-500 uppercase tracking-[0.3em] text-sm">Profile Overview</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-12 items-start">
            <div className="md:col-span-12 glass-card p-10 md:p-14 space-y-8 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-neon-cyan/5 blur-3xl group-hover:bg-neon-cyan/10 transition-colors" />

              <p className="text-xl md:text-2xl text-gray-300 font-light leading-relaxed">
                Elite cybersecurity engineer focused on <span className="text-white font-medium italic">protecting critical infrastructure</span>.
                With technical depth in AI-powered defense, SOC operations, and advanced threat hunting,
                I build digital shells that evolve faster than the threats they stop.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-8 border-t border-white/5">
                {[
                  { label: 'Education', val: 'B.E CSE (Cybersecurity)', icon: '🎓', color: 'text-neon-cyan' },
                  { label: 'Certifications', val: 'Google Cybersecurity | Cisco EH', icon: '🏆', color: 'text-neon-red' },
                  { label: 'Core Focus', val: 'AI Security & Threat Intelligence', icon: '🎯', color: 'text-neon-purple' },
                  { label: 'Location', val: 'Coimbatore, India', icon: '📍', color: 'text-neon-cyan' }
                ].map((item, i) => (
                  <motion.div
                    key={i}
                    whileHover={{ x: 10 }}
                    className="space-y-2 group/item"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg">{item.icon}</span>
                      <h3 className={`${item.color} font-bold text-sm uppercase tracking-widest`}>{item.label}</h3>
                    </div>
                    <p className="text-gray-400 font-medium">{item.val}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
