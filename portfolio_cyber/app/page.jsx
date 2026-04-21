'use client'

import { useState } from 'react'
import Hero from '../components/Hero'
import About from '../components/About'
import Skills from '../components/Skills'
import Projects from '../components/Projects'
import Achievements from '../components/Achievements'
import Contact from '../components/Contact'
import Footer from '../components/Footer'
import Particles from '../components/Particles'
import LoadingScreen from '../components/LoadingScreen'
import VoiceAssistant from '../components/VoiceAssistant'

export default function Home() {
  const [isLoading, setIsLoading] = useState(true)

  return (
    <main className={`w-full bg-dark-bg transition-opacity duration-1000 ${isLoading ? 'opacity-0' : 'opacity-100'}`}>
      <LoadingScreen onComplete={() => setIsLoading(false)} />

      {!isLoading && (
        <div className="scanlines cyber-grid">
          <VoiceAssistant />
          <Particles />
          <Hero />
          <About />
          <Skills />
          <Projects />
          <Achievements />
          <Contact />
          <Footer />
        </div>
      )}
    </main>
  )
}
