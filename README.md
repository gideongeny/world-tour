# 🌍 World Tour - Travel Booking Platform

A modern, full-stack travel booking application with AI-powered recommendations, multi-currency support, and real-time data.

![World Tour](https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&q=80&w=1200)

## ✨ Features

### 🔐 Authentication System
- User registration and login
- User Profile Dashboard
- Saved Trips & Wishlist

### 💱 Multi-Currency Support
- **9 Currencies**: USD, EUR, GBP, KES, ZAR, etc.
- Real-time exchange rates

### 🏨 Travel Services
- **Destinations**: 32+ world-class locations
- **Hotels**: Booking.com / Google Hotels integration
- **Flights**: Scanner/Kayak integration
- **AI Assistant**: Gemini-powered planning

### 💰 Monetization
- **Affiliate System**: Booking.com, Skyscanner, etc.
- **Premium Subscription**: PayPal / Stripe integration
- **Ad Network**: Monetag integration

## 🚀 Quick Start (Local)

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run server (http://localhost:5000)
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:5173
```

## 📦 Deployment Guide (Vercel)

This project is configured for **Vercel Monorepo Deployment** (Frontend + Backend in one project).

### Step 1: Push to GitHub
Ensure your code is pushed to your GitHub repository.

### Step 2: Import to Vercel
1. Go to [Vercel Dashboard](https://vercel.com).
2. Click **Add New** > **Project**.
3. Import your `world-tour` repository.

### Step 3: Configure Project
- **Framework Preset**: Vite (should auto-detect).
- **Root Directory**: `./` (Keep default).
- **Build Command**: `npm run build` (in frontend).
- **Output Directory**: `frontend/dist`.

> **Note**: The included `vercel.json` handles the routing between Frontend and Backend automatically!

### Step 4: Environment Variables (Critical!)
Add these in Vercel **Settings > Environment Variables**:

**Application:**
- `FLASK_ENV`: `production`
- `SECRET_KEY`: (Generate a random string)
- `FRONTEND_URL`: `https://your-project-name.vercel.app` (Your production Vercel URL)

**Database (Neon/Postgres):**
- `DATABASE_URL`: `postgres://user:password@host/dbname?sslmode=require`
*(If using Neon, it provides this connection string)*

**Monetization Keys:**
- `PAYPAL_CLIENT_ID`: (From PayPal Developer)
- `PAYPAL_CLIENT_SECRET`: (From PayPal Developer)
- `PAYPAL_MODE`: `live` (or `sandbox`)
- `STRIPE_SECRET_KEY`: (Optional)
- `STRIPE_PUBLISHABLE_KEY`: (Optional)

**Affiliate IDs:**
- `BOOKING_COM_AFFILIATE_ID`
- `SKYSCANNER_AFFILIATE_ID`

**AI:**
- `GOOGLE_API_KEY`: (Gemini API Key)

### Step 5: Deploy
Click **Deploy**. Vercel will build the frontend and set up the serverless backend.

### ⚠️ Common Issues
- **"Backend Not Connected"**: Ensure you added `FRONTEND_URL` and `DATABASE_URL`.
- **"Database Error"**: Verify your Neon connection string.
- **"CORS Error"**: This template uses relative paths (`/api/...`), so CORS is usually not an issue if deployed as a single project.

---

**Built with ❤️ using React, Flask, and AI**
