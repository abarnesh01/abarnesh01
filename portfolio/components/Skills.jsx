'use client'

import { motion } from 'framer-motion'

const skills = [
  { category: 'CYBER DEFENSE', icon: '🛡️', items: ['Network Security', 'SIEM', 'Threat Detection', 'SOC Operations', 'Ethical Hacking', 'Penetration Testing'] },
  { category: 'SYSTEM ARCHITECTURE', icon: '⚙️', items: ['Python', 'JavaScript', 'Java', 'FastAPI', 'Express.js', 'React'] },
  { category: 'INTELCORE (AI)', icon: '🧠', items: ['Computer Vision', 'OpenCV', 'EasyOCR', 'Anomaly Detection', 'Neural Networks', 'Data Science'] },
  { category: 'INFRASTRUCTURE', icon: '🛰️', items: ['Git', 'Docker', 'Linux', 'SQL', 'VS Code', 'CI/CD'] },
]

export default function Skills() {
  return (
    <section id="skills" className="min-h-screen flex items-center justify-center bg-dark-bg py-24 relative">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-neon-red/5 rounded-full blur-[150px] translate-x-1/2 -translate-y-1/2" />

      <div className="container mx-auto px-6 relative z-10 w-full">
        <div className="flex flex-col items-center mb-16 text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-4 tracking-tighter">
            SKILL <span className="text-neon-cyan neon-text">MODULES</span>
          </h2>
          <p className="text-gray-500 uppercase tracking-[0.3em] text-sm">Competency Matrix</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {skills.map((skillGroup, idx) => (
            <motion.div
              key={idx}
              className="glass-card p-10 relative overflow-hidden group border-white/5"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="flex items-center gap-4 mb-8">
                <span className="text-2xl">{skillGroup.icon}</span>
                <h3 className="text-xl font-bold tracking-widest text-white group-hover:text-neon-cyan transition-colors uppercase">
                  {skillGroup.category}
                </h3>
              </div>

              <div className="flex flex-wrap gap-3">
                {skillGroup.items.map((skill, i) => (
                  <motion.span
                    key={i}
                    className="px-4 py-2 bg-white/5 rounded-lg border border-white/10 text-gray-400 text-sm font-medium hover:border-neon-cyan hover:text-white transition-all duration-300 cursor-default"
                    whileHover={{
                      scale: 1.05,
                      backgroundColor: 'rgba(0, 245, 255, 0.1)',
                      boxShadow: '0 0 15px rgba(0, 245, 255, 0.2)'
                    }}
                  >
                    {skill}
                  </motion.span>
                ))}
              </div>

              {/* Decorative Corner */}
              <div className="absolute top-0 right-0 w-8 h-8 pointer-events-none">
                <div className="absolute top-0 right-0 h-[1px] w-full bg-neon-cyan/50" />
                <div className="absolute top-0 right-0 w-[1px] h-full bg-neon-cyan/50" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
