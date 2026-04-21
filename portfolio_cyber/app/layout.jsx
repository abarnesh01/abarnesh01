import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Abarnesh S - Cybersecurity Engineer',
  description: 'Elite SOC Analyst | Security Researcher | Full Stack Developer',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-dark-bg text-white`}>
        {children}
      </body>
    </html>
  )
}
