'use client'

import { motion } from 'framer-motion'

const achievements = [
  {
    year: '2026',
    title: 'Breach Point National Level CTF',
    issuer: 'Malla Reddy University',
    description: '24-hour cybersecurity competition. Solved challenges in Web Security, Cryptography & Linux',
    icon: '🏆',
  },
  {
    year: '2025',
    title: 'Google Cybersecurity Professional',
    issuer: 'Google',
    description: 'Comprehensive security certification covering network security, threats & SIEM concepts',
    icon: '📜',
  },
  {
    year: '2025',
    title: 'Cisco Ethical Hacking',
    issuer: 'Cisco Systems',
    description: 'Advanced penetration testing and ethical hacking certification (CEH equivalent)',
    icon: '🎖️',
  },
]

export default function Achievements() {
  return (
    <section id="achievements" className="min-h-screen flex items-center justify-center bg-gradient-dark py-20">
      <div className="max-w-4xl mx-auto px-4 w-full">
        <motion.h2
          className="text-5xl md:text-6xl font-bold mb-16 text-center text-neon-cyan neon-text"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          Achievements
        </motion.h2>

        <div className="space-y-8">
          {achievements.map((achievement, idx) => (
            <motion.div
              key={idx}
              className="glass p-8 rounded-lg border-l-4 border-neon-red hover-glow"
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.2, duration: 0.6 }}
            >
              <div className="flex items-start gap-6">
                <div className="text-5xl">{achievement.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-4 mb-2">
                    <h3 className="text-2xl font-bold text-neon-cyan">{achievement.title}</h3>
                    <span className="text-sm px-3 py-1 bg-neon-red text-dark-bg rounded font-bold">
                      {achievement.year}
                    </span>
                  </div>
                  <p className="text-neon-red text-sm mb-3">{achievement.issuer}</p>
                  <p className="text-gray-300">{achievement.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
