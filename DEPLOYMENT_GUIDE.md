# 🌐 Deployment Guide

## Choose Your Platform

### ⚡ Vercel (Easiest - Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd portfolio
vercel
```

**Features:**
- ✅ Free tier
- ✅ Auto-deploys on git push
- ✅ Custom domain
- ✅ SSL certificate
- ✅ Analytics included

---

### 🚀 Netlify

1. Go to [netlify.com](https://netlify.com)
2. Connect GitHub repo
3. Build settings:
   - Build command: `npm run build`
   - Publish: `.next`
4. Deploy!

**Features:**
- ✅ Free tier
- ✅ Git integration
- ✅ Continuous deployment
- ✅ Form handling

---

### 📦 GitHub Pages

```bash
# Static export
npm run build

# Create gh-pages branch
git checkout -b gh-pages
git add -A
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

Go to Settings → Pages → Select `gh-pages` branch

---

### 🐳 Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY .next .next
COPY public public

EXPOSE 3000

CMD ["npm", "start"]
```

Build & run:

```bash
docker build -t cybersecurity-portfolio .
docker run -p 3000:3000 cybersecurity-portfolio
```

---

### 📍 Custom VPS (AWS, DigitalOcean, etc)

1. SSH into server
2. Clone repo
3. Install Node.js
4. Run:
   ```bash
   npm install
   npm run build
   npm start
   ```
5. Setup nginx reverse proxy
6. Use PM2 for process management

---

## Custom Domain Setup

### Vercel

1. Go to Project Settings
2. Domains
3. Add custom domain
4. Follow DNS instructions

### Netlify

1. Site settings
2. Domain management
3. Add custom domain
4. Update DNS records

### Generic (All platforms)

Add these DNS records:

```
Type: CNAME
Name: www
Value: your-site.vercel.app

Type: A
Name: @
Value: 76.76.19.20 (Vercel's IP)
```

---

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_SITE_URL=https://abarnesh.dev
NEXT_PUBLIC_GITHUB_USERNAME=abarnesh
```

Use in components:

```js
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL
```

---

## SSL Certificate

All platforms provide free SSL. No additional setup needed!

---

## Performance Monitoring

### Vercel Analytics

Built-in dashboard showing:
- Performance metrics
- User analytics
- Error tracking

### Lighthouse CI

Add to GitHub Actions for CI/CD testing.

---

## Monitoring & Logs

### Vercel

Projects → Analytics → Live logs

### Netlify

Site info → Functions logs

### VPS

```bash
pm2 logs
tail -f /var/log/nginx/access.log
```

---

## Backup Strategy

```bash
# Daily backup to GitHub
git add -A
git commit -m "Auto backup"
git push origin main
```

---

**Ready to deploy? Pick a platform and go live! 🚀**
