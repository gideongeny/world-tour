# 🌍 World Tour - Travel Booking Platform

A modern, full-stack travel booking application with AI-powered recommendations, multi-currency support, and real-time data.

![World Tour](https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&q=80&w=1200)

## ✨ Features

### 🔐 Authentication System
- User registration and login
- Session persistence with localStorage
- Secure password hashing
- Visual user status in navigation

### 💱 Multi-Currency Support
- **9 Currencies**: USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, INR
- Real-time exchange rates from API
- Automatic price conversion
- Daily rate updates
- Persistent currency selection

### 🏨 Travel Services
- **Destinations**: Browse 32+ world-class destinations
- **Hotels**: Luxury accommodations worldwide
- **Flights**: International flight bookings
- **AI Assistant**: Gemini-powered travel recommendations

### 🎨 Modern UI/UX
- Responsive design (mobile, tablet, desktop)
- Dark mode support
- Glassmorphism effects
- Smooth animations and transitions
- Image fallbacks for offline support

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

Server runs on `http://localhost:5000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on `http://localhost:5173`

## 📁 Project Structure

```
world-tour-main/
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── context/         # React contexts (User, Currency)
│   │   ├── pages/           # Page components
│   │   └── App.tsx          # Main app component
│   └── vite.config.ts       # Vite configuration
│
├── blueprints/              # Flask blueprints
│   ├── auth/               # Authentication routes
│   ├── booking/            # Booking routes
│   └── ai/                 # AI assistant routes
│
├── services/               # Backend services
│   ├── ai_engine.py       # Gemini AI integration
│   ├── currency.py        # Currency conversion
│   └── weather.py         # Weather API
│
├── app.py                 # Flask application
├── new_models.py          # SQLAlchemy models
└── requirements.txt       # Python dependencies
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Routing**: React Router v6
- **Icons**: Lucide React
- **State**: Context API

### Backend
- **Framework**: Flask
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **AI**: Google Gemini API
- **Deployment**: Vercel

## 🔑 Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key
GOOGLE_API_KEY=your-gemini-api-key
DATABASE_URL=your-database-url
STRIPE_SECRET_KEY=your-stripe-key
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000
```

## 📖 API Documentation

### Authentication
- `POST /auth/register` - Create new account
- `POST /auth/login` - Login user
- `GET /auth/logout` - Logout user

### Booking
- `GET /booking/destinations` - Get all destinations
- `GET /booking/hotels` - Get all hotels
- `GET /booking/flights` - Get all flights
- `POST /booking/book/:id` - Create booking

### Currency
- `GET /api/currency/rates` - Get exchange rates

### AI
- `POST /ai/api/chat` - Chat with AI assistant

## 🎯 Usage Examples

### Currency Conversion
```typescript
import { useCurrency } from './context/CurrencyContext';

function PriceDisplay() {
  const { formatPrice } = useCurrency();
  return <span>{formatPrice(200)}</span>; // Converts to selected currency
}
```

### Authentication
```typescript
import { useUser } from './context/UserContext';

function Profile() {
  const { user, isAuthenticated, logout } = useUser();
  
  if (!isAuthenticated) return <Login />;
  
  return (
    <div>
      <h1>Welcome, {user.username}!</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

## 🧪 Testing

```bash
# Run backend tests
python -m pytest

# Run frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Vercel (Recommended)

1. **Backend**: Deploy to Vercel Serverless Functions
2. **Frontend**: Deploy to Vercel Static Hosting

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Manual Deployment

```bash
# Build frontend
cd frontend
npm run build

# Serve with Flask
python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Unsplash](https://unsplash.com) - Images
- [Lucide](https://lucide.dev) - Icons
- [TailwindCSS](https://tailwindcss.com) - Styling
- [Google Gemini](https://ai.google.dev) - AI Integration
- [Exchange Rate API](https://exchangerate-api.com) - Currency Rates

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using React, Flask, and AI**
