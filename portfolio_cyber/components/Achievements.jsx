'use client'

import { motion } from 'framer-motion'

const achievements = [
  {
    year: '2026',
    title: 'BREACH POINT NATIONAL CTF',
    issuer: 'Malla Reddy University',
    description: '24-hour cybersecurity competition. Domain: Web Security, Cryptography & Linux.',
    icon: '🏆',
  },
  {
    year: '2025',
    title: 'GOOGLE CYBERSECURITY PROF',
    issuer: 'Google Corp',
    description: 'Advanced network security, threat intelligence, and SIEM infrastructure.',
    icon: '📜',
  },
  {
    year: '2025',
    title: 'CISCO ETHICAL HACKING',
    issuer: 'Cisco Networking Academy',
    description: 'Advanced penetration testing and offensive security operations.',
    icon: '🎖️',
  },
]

export default function Achievements() {
  return (
    <section id="achievements" className="min-h-screen flex items-center justify-center bg-dark-bg py-24 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="container mx-auto px-6 relative z-10 w-full">
        <div className="flex flex-col items-center mb-20 text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-4 tracking-tighter">
            SYSTEM <span className="text-neon-cyan neon-text">LOGS</span>
          </h2>
          <p className="text-gray-500 uppercase tracking-[0.3em] text-sm">Merits & Verification</p>
        </div>

        <div className="max-w-5xl mx-auto space-y-8">
          {achievements.map((achievement, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.2, duration: 1, ease: [0.16, 1, 0.3, 1] }}
              className="glass-card p-10 flex flex-col md:flex-row items-center gap-10 group hover:border-neon-red/50 transition-all border-white/5"
            >
              <div className="text-6xl group-hover:scale-110 transition-transform duration-500">{achievement.icon}</div>
              <div className="flex-1 text-center md:text-left space-y-4">
                <div className="flex flex-col md:flex-row items-center gap-4">
                  <h3 className="text-2xl font-bold text-white tracking-widest uppercase">{achievement.title}</h3>
                  <span className="px-4 py-1 bg-white/5 border border-white/10 text-neon-red text-xs font-black rounded-full">
                    {achievement.year}
                  </span>
                </div>
                <p className="text-neon-cyan/80 text-sm font-bold tracking-widest uppercase italic">{achievement.issuer}</p>
                <p className="text-gray-400 font-light text-lg">{achievement.description}</p>
              </div>

              {/* Status Indicator */}
              <div className="hidden md:flex flex-col items-end gap-2">
                <div className="w-12 h-1 bg-neon-cyan/20 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ x: '-100%' }}
                    whileInView={{ x: '0%' }}
                    transition={{ duration: 1.5, delay: idx * 0.3 }}
                    className="w-full h-full bg-neon-cyan"
                  />
                </div>
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Verified</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
