# 🌍 World Tour - Premium Travel Platform

A next-generation travel booking application featuring 3D visualization, AI-powered planning, and seamless payments.

## 🟢 Live Demo
**Website**: [https://world-tour-f6f23.web.app/](https://world-tour-f6f23.web.app/)

![World Tour](https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&q=80&w=1200)

---

## ✨ New Features (Jan 2026 Update)

### 💳 Enhanced Payment System
- **PayPal Integration**: Users can now choose between **Credit Card (Stripe)** and **PayPal** at checkout.
- **Smart Checkout**: Dynamic payment method switching with secure processing.

### 🌍 Global Satellite View
- **Interactive 3D Map**: A full-width, edge-to-edge satellite map integrated into the homepage.
- **Real-time Markers**: Visualizes all 19+ available destinations globally.

### 🤖 Advanced AI Assistant
- **Real API Integration**: The AI now connects to backend services (OpenAI) instead of using mock responses.
- **Personalized Planning**: Generates custom itineraries based on user preferences.

### 📱 Perfect Mobile Experience
- **Responsive Layout**: Fixed horizontal scrolling issues on Android.
- **Optimized UI**: Typography and spacing adjusted for all screen sizes.

### 🔐 Full Authentication
- **Traveler Signup**: Complete registration flow integrated with the backend.
- **Secure Sessions**: Protected routes for profile and booking management.

---

## 🛠️ Architecture & Deployment

This project uses a **Hybrid Cloud Architecture**:

- **Frontend**: Hosted on **Firebase Hosting** (CDNs for speed).
- **Backend**: Hosted on **Render** (Python/Flask API).
- **Database**: **SQLite** (Development) / **PostgreSQL** (Recommended for Production).

### ⚠️ Important Note on Data
The current backend on Render uses an ephemeral file system. **This means the database resets when the server restarts.**
To fix this permanently for production, connect a remote PostgreSQL database (like Neon or Render Postgres) by setting the `DATABASE_URL` environment variable.

### Deployment Commands

**1. Deploy Frontend (Firebase)**
```bash
cd frontend
npm run build
cd ..
firebase deploy
```

**2. Manage Backend**
The backend auto-deploys from GitHub. To restore data after a restart:
```bash
# Seed the database manually if needed
curl https://world-tour-ngmj.onrender.com/seed
```

---

## 💻 Local Development

### Quick Start (Run Both Backend & Frontend Together)

**Option 1: Using the Start Script (Recommended)**
```bash
# Windows
start_dev.bat

# Mac/Linux
python start_dev.py
```

**Option 2: Using npm (requires npm install in root)**
```bash
npm install
npm start
```

**Option 3: Manual Start (Separate Terminals)**

Backend:
```bash
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

The start scripts automatically:
- ✅ Check if Python and Node.js are installed
- ✅ Install dependencies if needed
- ✅ Run both backend and frontend simultaneously
- ✅ Color-coded terminal output for easy debugging

---

**Built with ❤️ using React, Flask, and AI**
