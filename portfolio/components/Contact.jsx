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
  }

  return (
    <section id="contact" className="min-h-screen flex items-center justify-center bg-dark-secondary py-20">
      <div className="max-w-3xl mx-auto px-4 w-full">
        <motion.h2
          className="text-5xl md:text-6xl font-bold mb-16 text-center text-neon-cyan neon-text"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          Get In Touch
        </motion.h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Contact Info */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-6"
          >
            <div className="glass p-6 rounded-lg border border-neon-cyan border-opacity-20 hover-glow">
              <h3 className="text-neon-cyan font-bold mb-2">📧 Email</h3>
              <p className="text-gray-300">abarnesh772@gmail.com</p>
            </div>

            <div className="glass p-6 rounded-lg border border-neon-red border-opacity-20 hover-glow">
              <h3 className="text-neon-red font-bold mb-2">💼 LinkedIn</h3>
              <a href="https://linkedin.com/in/abarnesh" className="text-gray-300 hover:text-neon-cyan transition">
                linkedin.com/in/abarnesh
              </a>
            </div>

            <div className="glass p-6 rounded-lg border border-neon-purple border-opacity-20 hover-glow">
              <h3 className="text-neon-purple font-bold mb-2">🐙 GitHub</h3>
              <a href="https://github.com/abarnesh" className="text-gray-300 hover:text-neon-cyan transition">
                github.com/abarnesh
              </a>
            </div>
          </motion.div>

          {/* Contact Form */}
          <motion.form
            onSubmit={handleSubmit}
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="glass p-8 rounded-lg border border-neon-cyan border-opacity-20 space-y-4"
          >
            <div>
              <label className="block text-neon-cyan text-sm mb-2">Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full bg-dark-bg border border-neon-cyan border-opacity-30 rounded px-4 py-2 text-white focus:outline-none focus:border-neon-cyan transition"
                required
              />
            </div>

            <div>
              <label className="block text-neon-cyan text-sm mb-2">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full bg-dark-bg border border-neon-cyan border-opacity-30 rounded px-4 py-2 text-white focus:outline-none focus:border-neon-cyan transition"
                required
              />
            </div>

            <div>
              <label className="block text-neon-cyan text-sm mb-2">Message</label>
              <textarea
                name="message"
                value={formData.message}
                onChange={handleChange}
                rows="4"
                className="w-full bg-dark-bg border border-neon-cyan border-opacity-30 rounded px-4 py-2 text-white focus:outline-none focus:border-neon-cyan transition resize-none"
                required
              />
            </div>

            <motion.button
              type="submit"
              className="w-full bg-neon-cyan text-black font-bold py-3 rounded hover:bg-neon-red transition"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Send Message
            </motion.button>
          </motion.form>
        </div>
      </div>
    </section>
  )
}
