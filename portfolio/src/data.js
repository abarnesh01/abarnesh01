export const listTools = [
  { id: 1, nama: 'Python', ket: 'Language', icon: 'python/python-original.svg', level: 90, color: '#3776AB' },
  { id: 2, nama: 'JavaScript', ket: 'Language', icon: 'javascript/javascript-original.svg', level: 85, color: '#F7DF1E' },
  { id: 3, nama: 'Bash', ket: 'Scripting', icon: 'bash/bash-original.svg', level: 80, color: '#4EAA25' },
  { id: 4, nama: 'Linux', ket: 'OS / Daily Driver', icon: 'linux/linux-original.svg', level: 85, color: '#FCC624' },
  { id: 5, nama: 'React', ket: 'Frontend Framework', icon: 'react/react-original.svg', level: 75, color: '#61DAFB' },
  { id: 6, nama: 'FastAPI', ket: 'Backend Framework', icon: 'fastapi/fastapi-original.svg', level: 70, color: '#05998B' },
  { id: 7, nama: 'Node.js', ket: 'Backend Framework', icon: 'nodejs/nodejs-original.svg', level: 75, color: '#339933' },
  { id: 8, nama: 'OpenCV', ket: 'Image Processing', icon: 'opencv/opencv-original.svg', level: 65, color: '#5C3EE8' },
  { id: 9, nama: 'Docker', ket: 'Containerization', icon: 'docker/docker-original.svg', level: 60, color: '#2496ED' },
  { id: 10, nama: 'Git', ket: 'Version Control', icon: 'git/git-original.svg', level: 85, color: '#F05032' },
  { id: 11, nama: 'EasyOCR', ket: 'OCR Framework', icon: 'python/python-original.svg', level: 65, color: '#3776AB' },
  { id: 12, nama: 'SIEM', ket: 'SOC / Security', icon: 'linux/linux-original.svg', level: 70, color: '#FCC624' }
];

export const listProyek = [
  {
    id: 1,
    title: 'Personal Information Masking Tool',
    subtitle: 'OCR-based PII masking system',
    description: 'A high-accuracy tool to auto-detect and mask PII in identity documents using OCR and OpenCV. Features real-time processing and secure data handling.',
    tags: ['Python', 'EasyOCR', 'OpenCV', 'FastAPI'],
    image: '/assets/proyek/proyek1.webp',
    github: 'https://github.com/abarnesh',
    demo: '#',
    color: '#00f5ff'
  },
  {
    id: 2,
    title: 'Civic AI Shield',
    subtitle: 'AI-powered CCTV monitoring',
    description: 'Real-time AI application for surveillance threat detection. Uses advanced deep learning models to identify anomalies and automated public safety alerts.',
    tags: ['AI', 'PyTorch', 'React', 'Socket.io'],
    image: '/assets/proyek/proyek2.webp',
    github: 'https://github.com/abarnesh',
    demo: '#',
    color: '#ff0040'
  },
  {
    id: 3,
    title: 'AI Network Traffic Monitoring',
    subtitle: 'ML anomaly detection system',
    description: 'A comprehensive SOC simulation tool that monitors live network traffic. Utilizes Scikit-Learn to detect potential security threats in real-time.',
    tags: ['Express.js', 'React', 'Scikit-Learn', 'D3.js'],
    image: '/assets/proyek/proyek3.webp',
    github: 'https://github.com/abarnesh',
    demo: '#',
    color: '#8a2be2'
  }
];
