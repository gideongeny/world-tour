import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import { CurrencyProvider } from './context/CurrencyContext';
import Nav from './components/Nav';
import MonetagManager from './components/MonetagManager';
import Home from './pages/Home';
import Hotels from './pages/Hotels';
import Flights from './pages/Flights';
import AIAssistant from './pages/AIAssistant';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Privacy from './pages/Privacy';
import Terms from './pages/Terms';
import Cookies from './pages/Cookies';
import Contact from './pages/Contact';
import Checkout from './pages/Checkout';
import Pricing from './pages/Pricing';
import SubscriptionSuccess from './pages/SubscriptionSuccess';
import Profile from './pages/Profile';
import TravelCards from './pages/TravelCards';


import { LanguageProvider, useLanguage } from './context/LanguageContext';

function AppContent() {
  const { t } = useLanguage();

  return (
    <UserProvider>
      <CurrencyProvider>
        <MonetagManager />
        <Router>
          <div className="min-h-screen bg-background text-slate-900 dark:text-white font-sans selection:bg-primary/20 relative">
            <div className="magical-texture"></div>
            <Nav />

            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/hotels" element={<Hotels />} />
              <Route path="/flights" element={<Flights />} />
              <Route path="/ai-assistant" element={<AIAssistant />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/privacy" element={<Privacy />} />
              <Route path="/terms" element={<Terms />} />
              <Route path="/cookies" element={<Cookies />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/subscription/success" element={<SubscriptionSuccess />} />
              <Route path="/travel-cards" element={<TravelCards />} />
            </Routes>

            <footer className="py-12 px-6 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 mt-auto">
              <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8 text-slate-500 dark:text-slate-400">
                <div className="text-2xl font-black text-slate-900 dark:text-white">
                  WORLD<span className="text-primary">TOUR</span>
                </div>
                <p>{t('footer.rights')}</p>
                <div className="flex gap-8">
                  <Link to="/privacy" className="hover:text-primary transition-colors">{t('footer.privacy')}</Link>
                  <Link to="/terms" className="hover:text-primary transition-colors">{t('footer.terms')}</Link>
                  <Link to="/cookies" className="hover:text-primary transition-colors">{t('footer.cookies')}</Link>
                </div>
              </div>
            </footer>
          </div>
        </Router>
      </CurrencyProvider>
    </UserProvider>
  )
}

function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  )
}

export default App
