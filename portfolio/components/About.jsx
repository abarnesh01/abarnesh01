'use client'

import { motion } from 'framer-motion'

export default function About() {
  return (
    <section id="about" className="min-h-screen flex items-center justify-center bg-dark-secondary py-20">
      <div className="max-w-4xl mx-auto px-4">
        <motion.h2
          className="text-5xl md:text-6xl font-bold mb-12 text-center text-neon-cyan neon-text"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          About Me
        </motion.h2>

        <motion.div
          className="glass p-8 rounded-lg mb-8 border border-neon-cyan border-opacity-20 hover-glow"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <p className="text-lg text-gray-200 mb-6">
            I'm an elite cybersecurity engineer with a passion for protecting critical infrastructure
            and detecting sophisticated threats. With expertise in AI-powered security solutions, SOC
            operations, and penetration testing, I combine technical depth with strategic security thinking.
          </p>

          <p className="text-lg text-gray-200 mb-6">
            My work spans threat detection systems, network security, and machine learning-based anomaly
            detection. I compete in CTFs at the national level and continuously advance my skills in
            emerging security technologies.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.div
              className="border-l-4 border-neon-cyan pl-4"
              whileHover={{ x: 10 }}
            >
              <h3 className="text-neon-cyan font-bold mb-2">🎓 Education</h3>
              <p className="text-gray-300">B.E CSE (Cybersecurity) @ KGISL Institute of Technology</p>
            </motion.div>

            <motion.div
              className="border-l-4 border-neon-red pl-4"
              whileHover={{ x: 10 }}
            >
              <h3 className="text-neon-red font-bold mb-2">🏆 Certifications</h3>
              <p className="text-gray-300">Google Cybersecurity Professional | Cisco Ethical Hacking</p>
            </motion.div>

            <motion.div
              className="border-l-4 border-neon-purple pl-4"
              whileHover={{ x: 10 }}
            >
              <h3 className="text-neon-purple font-bold mb-2">🎯 Focus</h3>
              <p className="text-gray-300">AI Security, Threat Detection, SOC Systems</p>
            </motion.div>

            <motion.div
              className="border-l-4 border-neon-cyan pl-4"
              whileHover={{ x: 10 }}
            >
              <h3 className="text-neon-cyan font-bold mb-2">📍 Location</h3>
              <p className="text-gray-300">Coimbatore, India</p>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
