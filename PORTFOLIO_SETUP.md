# 🚀 Portfolio Setup Guide

## Quick Start

### 1️⃣ Install Dependencies

```bash
cd portfolio
npm install
```

### 2️⃣ Run Development Server

```bash
npm run dev
```

Visit `http://localhost:3000`

### 3️⃣ Build for Production

```bash
npm run build
npm start
```

---

## 📁 Project Structure

```
portfolio/
├── app/
│   ├── layout.jsx          # Root layout
│   ├── page.jsx            # Home page
│   └── globals.css         # Global styles
├── components/
│   ├── Hero.jsx            # Hero section
│   ├── About.jsx           # About section
│   ├── Skills.jsx          # Skills showcase
│   ├── Projects.jsx        # Project cards
│   ├── Achievements.jsx    # Achievements timeline
│   ├── Contact.jsx         # Contact form
│   └── Footer.jsx          # Footer
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind config
├── next.config.js          # Next.js config
└── postcss.config.js       # PostCSS config
```

---

## 🎨 Customization

### Colors

Edit `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      'neon-cyan': '#00f5ff',    // Primary
      'neon-red': '#ff0040',     // Secondary
      'neon-purple': '#8a2be2',  // Accent
    }
  }
}
```

### Content

Edit component files in `components/` folder:
- `Hero.jsx` - Hero text & CTA
- `About.jsx` - Bio & details
- `Projects.jsx` - Project cards
- etc.

### Animations

Framer Motion is used. Customize in component `whileHover`, `animate`, `transition` props.

---

## 🚀 Deployment

### Vercel (Recommended)

```bash
npx vercel
```

Follow prompts and it's live!

### Netlify

1. Connect GitHub repo
2. Set build command: `npm run build`
3. Set publish directory: `.next`

### GitHub Pages

Build static export:

```bash
npm run build
npm run export
```

---

## 🔄 GitHub Actions Auto-Update

The repo includes `.github/workflows/update-readme.yml` that:
- Runs daily at midnight UTC
- Fetches latest 5 commits
- Updates README with recent activity

No additional setup needed!

---

## 📊 Performance Optimization

- Image optimization with Next.js Image
- Code splitting automatic
- CSS minification
- Font optimization

---

## 🐛 Troubleshooting

### Port 3000 already in use

```bash
npm run dev -- -p 3001
```

### Build errors

Clear cache:

```bash
rm -rf .next node_modules package-lock.json
npm install
npm run build
```

### CSS not loading

Reinstall Tailwind:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

## 📞 Support

Questions? Check:
- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind Docs](https://tailwindcss.com/docs)
- [Framer Motion Docs](https://www.framer.com/motion/)

---

**Happy coding! 🚀**
