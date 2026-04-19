'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'

export default function Contact() {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' })

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // Handle form submission
    console.log(formData)
    setFormData({ name: '', email: '', message: '' })
    alert("System Uplink Established: Message Received.")
  }

  const contacts = [
    { label: 'Uplink (Email)', val: 'abarnesh772@gmail.com', href: 'mailto:abarnesh772@gmail.com', icon: '📧', color: 'text-neon-cyan' },
    { label: 'Nexus (LinkedIn)', val: 'abarnesh-s', href: 'https://www.linkedin.com/in/abarnesh-s-106a34314/', icon: '💼', color: 'text-neon-cyan' },
    { label: 'Terminal (GitHub)', val: 'abarnesh01', href: 'https://github.com/abarnesh01', icon: '🐙', color: 'text-neon-purple' },
    { label: 'Secure Line (Phone)', val: '+91 99442 54589', href: 'tel:+919944254589', icon: '📞', color: 'text-neon-red' }
  ]

  return (
    <section id="contact" className="min-h-screen flex items-center justify-center bg-dark-bg py-24 relative overflow-hidden">
      <div className="absolute bottom-0 left-0 w-full h-[500px] bg-neon-purple/5 blur-[120px] pointer-events-none" />

      <div className="container mx-auto px-6 relative z-10">
        <div className="flex flex-col items-center mb-20 text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-4 tracking-tighter">
            ESTABLISH <span className="text-neon-cyan neon-text">UPLINK</span>
          </h2>
          <p className="text-gray-500 uppercase tracking-[0.3em] text-sm">Communication Protocol</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 max-w-6xl mx-auto items-center">
          {/* Contact Info */}
          <div className="space-y-8">
            <h3 className="text-2xl font-bold text-white uppercase tracking-widest mb-10 border-l-2 border-neon-cyan pl-6">Core Relays</h3>
            <div className="grid grid-cols-1 gap-6">
              {contacts.map((c, i) => (
                <motion.a
                  key={i}
                  href={c.href}
                  initial={{ opacity: 0, x: -30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1, duration: 0.8 }}
                  viewport={{ once: true }}
                  className="glass-card p-6 flex items-center gap-6 group hover:border-neon-cyan transition-all"
                >
                  <div className="text-2xl w-12 h-12 flex items-center justify-center rounded-lg bg-white/5 border border-white/10 group-hover:text-neon-cyan group-hover:border-neon-cyan transition-all">
                    {c.icon}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">{c.label}</h4>
                    <p className="text-lg text-white font-medium group-hover:text-neon-cyan transition-colors">{c.val}</p>
                  </div>
                </motion.a>
              ))}
            </div>
          </div>

          {/* Contact Form */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1 }}
            viewport={{ once: true }}
            className="glass-card p-10 md:p-14 relative"
          >
            <form onSubmit={handleSubmit} className="space-y-8">
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em]">Identify (Name)</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-6 py-4 text-white focus:outline-none focus:border-neon-cyan transition-all font-light"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em]">Data Stream (Email)</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-6 py-4 text-white focus:outline-none focus:border-neon-cyan transition-all font-light"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em]">Transmission (Message)</label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  rows="4"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-6 py-4 text-white focus:outline-none focus:border-neon-cyan transition-all font-light resize-none"
                  required
                />
              </div>

              <motion.button
                type="submit"
                whileHover={{ scale: 1.02, boxShadow: '0 0 30px rgba(0, 245, 255, 0.3)' }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-5 bg-neon-cyan text-black font-black uppercase tracking-[0.3em] rounded-xl hover:bg-white transition-all duration-500"
              >
                Transmit Message
              </motion.button>
            </form>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
