# 🚀 Deploy to Vercel - Step by Step Guide

## Method 1: Deploy with Vercel CLI (Recommended)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Navigate to Project
```bash
cd blog-website
```

### Step 4: Deploy
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name? **my-blog** (or your choice)
- Directory? **./** (press Enter)

### Step 5: Deploy to Production
```bash
vercel --prod
```

---

## Method 2: Deploy with GitHub

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/my-blog.git
git push -u origin main
```

### Step 2: Import to Vercel
1. Go to https://vercel.com/dashboard
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect Flask settings
5. Click **"Deploy"**

---

## ⚠️ Important: Database Setup

Vercel uses **serverless functions** with an **ephemeral filesystem**. This means:

| Issue | Solution |
|-------|----------|
| SQLite won't persist | Use **Vercel Postgres** or **Neon** |
| Uploaded files disappear | Use **Vercel Blob** or **Cloudinary** |

### Option A: Use Vercel Postgres (Recommended)

1. Go to your Vercel project dashboard
2. Click **"Storage"** → **"Create Database"**
3. Select **"Postgres"**
4. Copy the connection string
5. Add to Environment Variables as `DATABASE_URL`

Update `app.py`:
```python
import os

database_url = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
# Fix for PostgreSQL URLs
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
```

### Option B: Use Neon (Free PostgreSQL)

1. Go to https://neon.tech
2. Create a free database
3. Copy the connection string
4. Add to Vercel Environment Variables

---

## 🔐 Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Random string (use `openssl rand -hex 32`) |
| `DATABASE_URL` | Your PostgreSQL connection string |
| `ADMIN_USERNAME` | admin |
| `ADMIN_PASSWORD` | Your secure password |

---

## 📁 Updated Project Structure

```
blog-website/
├── app.py              # Updated for Vercel
├── vercel.json         # Vercel configuration
├── requirements.txt    # Python dependencies
├── .vercelignore       # Files to exclude
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
└── templates/
    └── ...
```

---

## 🧪 Test Locally Before Deploying

```bash
# Install Vercel CLI
npm install -g vercel

# Run locally with Vercel
vercel dev
```

---

## 🔄 Auto-Deploy on Git Push

Once connected to GitHub:
- Push to `main` branch → Auto-deploys to production
- Push to other branches → Creates preview deployments

---

## 🌐 Custom Domain

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your domain (e.g., `myblog.com`)
3. Update DNS records at your registrar:
   - Type: `A` → Value: `76.76.21.21`
   - Type: `CNAME` → Value: `cname.vercel-dns.com`

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check `requirements.txt` has correct versions |
| Database errors | Use PostgreSQL, not SQLite |
| Static files missing | Check `vercel.json` routes |
| 500 errors | Check Vercel function logs |

---

## 📞 Need Help?

- Vercel Docs: https://vercel.com/docs
- Flask on Vercel: https://vercel.com/guides/deploying-a-flask-app
