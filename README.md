# 🌍 World Tour - Travel Booking Platform

A modern, full-stack travel booking application with AI-powered recommendations, multi-currency support, and real-time data.

## 🟢 Live Demo
**Website**: [https://world-tour-f6f23.web.app/](https://world-tour-f6f23.web.app/)

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

---

## 🛠️ Architecture

This project uses a **Hybrid Cloud Architecture** for maximum performance and zero cost:

- **Frontend**: Hosted on **Firebase Hosting** (Fast global CDN)
- **Backend**: Hosted on **Render.com** (Python/Flask API)
- **Database**: **Neon** (Serverless Postgres)

## 🚀 Deployment Guide

### 1. Backend (Render)
The backend runs on Render Web Services.
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Env Vars**: `DATABASE_URL`, `SECRET_KEY`, `OPENAI_API_KEY`

### 2. Frontend (Firebase)
The frontend connects to the backend via environmental variables.

**To Deploy Updates:**
```bash
# 1. Build the frontend
cd frontend
npm run build
cd ..

# 2. Deploy to Firebase
firebase deploy
```

---

## 💻 Local Development

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

---

**Built with ❤️ using React, Flask, and AI**
