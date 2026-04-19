/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'neon-cyan': '#00f5ff',
        'neon-red': '#ff0040',
        'neon-purple': '#8a2be2',
        'dark-bg': '#050505',
        'dark-secondary': '#0d1117',
      },
      backgroundImage: {
        'gradient-neon': 'linear-gradient(135deg, #00f5ff 0%, #ff0040 100%)',
        'gradient-dark': 'linear-gradient(135deg, #050505 0%, #0d1117 100%)',
      },
      boxShadow: {
        'neon-cyan': '0 0 20px rgba(0, 245, 255, 0.5)',
        'neon-red': '0 0 20px rgba(255, 0, 64, 0.5)',
        'neon-purple': '0 0 20px rgba(138, 43, 226, 0.5)',
      },
      animation: {
        'spin-slow': 'spin 8s linear infinite',
      },
    },
  },
  plugins: [],
}
