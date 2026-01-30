# 🚀 Deployment Instructions

Deploy your AI School Bus Routing System to the cloud for free!

## Overview
- **Frontend**: Vercel (Free tier)
- **Backend**: Render (Free tier)
- **Database**: SQLite (included) or PostgreSQL (Render add-on)

---

## 📦 Step 1: Deploy Backend to Render

### 1.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended)

### 1.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `AKSHAY-RAVIKUMAR-7/school-bus-routing-ai`
3. Configure the service:
   - **Name**: `school-bus-routing-api`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 1.3 Set Environment Variables
In Render dashboard, add these environment variables:
```
SECRET_KEY=your-random-secret-key-here-change-this
FLASK_ENV=production
FRONTEND_URL=https://school-bus-routing-ai.vercel.app
DATABASE_URL=sqlite:///school_bus.db
```

### 1.4 Deploy
1. Click **"Create Web Service"**
2. Wait 3-5 minutes for deployment
3. Copy your backend URL: `https://school-bus-routing-api.onrender.com`

> **Note**: Free tier sleeps after 15 minutes of inactivity. First request may take 30-60 seconds.

---

## 🌐 Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### 2.2 Import Project
1. Click **"Add New..."** → **"Project"**
2. Import your repository: `AKSHAY-RAVIKUMAR-7/school-bus-routing-ai`
3. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 2.3 Set Environment Variable
Add this environment variable in Vercel:
```
VITE_API_URL=https://school-bus-routing-api.onrender.com
```

### 2.4 Update Frontend API URL
Edit `frontend/src/pages/*.jsx` files to use environment variable:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
```

### 2.5 Deploy
1. Click **"Deploy"**
2. Wait 1-2 minutes
3. Your site will be live at: `https://school-bus-routing-ai.vercel.app`

---

## 🔄 Step 3: Update Backend CORS

After getting your Vercel URL, update the backend:

1. In Render dashboard, update environment variable:
   ```
   FRONTEND_URL=https://school-bus-routing-ai.vercel.app
   ```

2. Render will auto-redeploy with new settings

---

## ✅ Step 4: Test Your Deployment

1. Visit your frontend URL: `https://school-bus-routing-ai.vercel.app`
2. Check if the dashboard loads
3. Try the route optimization feature
4. Verify real-time tracking works

### Troubleshooting
- **Backend Error 503**: Free tier is waking up, wait 30 seconds
- **CORS Error**: Check `FRONTEND_URL` environment variable
- **API Not Responding**: Verify backend URL in Vercel environment variables

---

## 🎉 You're Live!

Your AI School Bus Routing System is now accessible worldwide:
- **Frontend**: `https://school-bus-routing-ai.vercel.app`
- **Backend API**: `https://school-bus-routing-api.onrender.com`

---

## 📊 Production Optimization (Optional)

### Add PostgreSQL Database (Recommended)
1. In Render dashboard, add PostgreSQL database (free tier available)
2. Copy the **Internal Database URL**
3. Update backend environment variable:
   ```
   DATABASE_URL=postgresql://user:password@...
   ```

### Add Redis (For Real-time Features)
1. Use [Redis Cloud](https://redis.com/try-free/) free tier
2. Get connection URL
3. Update environment variable:
   ```
   REDIS_URL=redis://default:password@...
   ```

### Enable HTTPS (Auto-enabled)
Both Vercel and Render provide free SSL certificates automatically.

---

## 🔧 Continuous Deployment

Any push to the `main` branch will automatically:
1. Trigger Vercel deployment (frontend)
2. Trigger Render deployment (backend)

Just commit and push:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

---

## 💰 Cost Breakdown

| Service | Free Tier | Cost After |
|---------|-----------|------------|
| Vercel | 100 GB bandwidth/month | $20/month |
| Render | 750 hours/month | $7/month |
| **Total** | **FREE** | **$27/month** |

---

## 📞 Support

- Vercel Issues: [vercel.com/support](https://vercel.com/support)
- Render Issues: [render.com/docs](https://render.com/docs)
- Project Issues: Open GitHub issue

---

**Congratulations! Your AI-powered school bus routing system is now deployed! 🎊**
