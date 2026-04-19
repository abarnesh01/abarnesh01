'use client'

import { motion } from 'framer-motion'

const skills = [
  { category: 'Cybersecurity', items: ['Network Security', 'SIEM', 'Threat Detection', 'SOC Operations', 'Ethical Hacking', 'Penetration Testing'] },
  { category: 'Development', items: ['Python', 'JavaScript', 'Java', 'FastAPI', 'Express.js', 'React'] },
  { category: 'AI & ML', items: ['Computer Vision', 'OpenCV', 'EasyOCR', 'Anomaly Detection', 'Neural Networks', 'Data Science'] },
  { category: 'Infrastructure', items: ['Git', 'Docker', 'Linux', 'SQL', 'VS Code', 'CI/CD'] },
]

export default function Skills() {
  return (
    <section id="skills" className="min-h-screen flex items-center justify-center bg-gradient-dark py-20">
      <div className="max-w-6xl mx-auto px-4 w-full">
        <motion.h2
          className="text-5xl md:text-6xl font-bold mb-16 text-center text-neon-cyan neon-text"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          Skills Arena
        </motion.h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {skills.map((skillGroup, idx) => (
            <motion.div
              key={idx}
              className="glass p-6 rounded-lg border border-neon-cyan border-opacity-20 hover-glow"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1, duration: 0.6 }}
            >
              <h3 className="text-2xl font-bold mb-4 text-neon-red">{skillGroup.category}</h3>
              <div className="flex flex-wrap gap-2">
                {skillGroup.items.map((skill, i) => (
                  <motion.span
                    key={i}
                    className="px-4 py-2 bg-dark-secondary rounded border border-neon-cyan border-opacity-40 text-neon-cyan text-sm"
                    whileHover={{ scale: 1.1, boxShadow: '0 0 20px rgba(0, 245, 255, 0.6)' }}
                  >
                    {skill}
                  </motion.span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
