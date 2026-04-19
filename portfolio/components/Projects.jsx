'use client'

import { motion } from 'framer-motion'

const projects = [
  {
    title: 'Personal Information Masking Tool',
    description: 'OCR-based system for detecting and redacting sensitive data from documents with 95%+ accuracy',
    tech: ['Python', 'EasyOCR', 'OpenCV'],
    color: 'from-neon-cyan to-blue-500',
    features: ['PII Detection', 'Auto Redaction', 'Batch Processing'],
  },
  {
    title: 'Civic AI Shield',
    description: 'Real-time AI-powered threat detection for public safety using CCTV analysis and computer vision',
    tech: ['Python', 'Computer Vision', 'React'],
    color: 'from-neon-red to-pink-500',
    features: ['CCTV Analysis', 'Threat Classification', 'Instant Alerts'],
  },
  {
    title: 'AI Network Traffic Dashboard',
    description: 'SOC analytics platform with ML-based anomaly detection for network monitoring',
    tech: ['Express.js', 'React', 'Machine Learning'],
    color: 'from-neon-purple to-purple-500',
    features: ['Flow Analysis', 'Anomaly Detection', 'Live Dashboard'],
  },
]

export default function Projects() {
  return (
    <section id="projects" className="min-h-screen flex items-center justify-center bg-dark-secondary py-20">
      <div className="max-w-6xl mx-auto px-4 w-full">
        <motion.h2
          className="text-5xl md:text-6xl font-bold mb-16 text-center text-neon-cyan neon-text"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          Featured Projects
        </motion.h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {projects.map((project, idx) => (
            <motion.div
              key={idx}
              className="group glass rounded-lg overflow-hidden border border-neon-cyan border-opacity-20 hover-glow cursor-pointer h-full flex flex-col"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.15, duration: 0.6 }}
              whileHover={{ y: -10 }}
            >
              {/* Header with gradient */}
              <div className={`h-40 bg-gradient-to-r ${project.color} opacity-20 group-hover:opacity-40 transition-opacity p-6 flex items-end`}>
                <h3 className="text-2xl font-bold text-white">{project.title}</h3>
              </div>

              {/* Content */}
              <div className="p-6 flex-1 flex flex-col">
                <p className="text-gray-300 mb-4">{project.description}</p>

                {/* Features */}
                <div className="mb-4 flex-1">
                  <div className="flex flex-wrap gap-2 mb-4">
                    {project.features.map((feature, i) => (
                      <span key={i} className="text-xs px-2 py-1 bg-dark-bg text-neon-cyan rounded border border-neon-cyan border-opacity-50">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Tech Stack */}
                <div className="border-t border-neon-cyan border-opacity-20 pt-4">
                  <p className="text-sm text-gray-400 mb-2">Tech Stack:</p>
                  <div className="flex flex-wrap gap-1">
                    {project.tech.map((tech, i) => (
                      <span key={i} className="text-xs text-neon-cyan">
                        {tech}
                        {i < project.tech.length - 1 && ' • '}
                      </span>
                    ))}
                  </div>
                </div>

                {/* View Link */}
                <motion.a
                  href="#"
                  className="mt-4 inline-flex items-center text-neon-cyan hover:text-neon-red transition"
                  whileHover={{ x: 5 }}
                >
                  View Project →
                </motion.a>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
