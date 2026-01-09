import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { Palette, LogOut, User as UserIcon } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const Nav: FC = () => {
    const [scrolled, setScrolled] = useState(false);
    const [monochrome, setMonochrome] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout, isAuthenticated } = useUser();
    const { language, setLanguage, t } = useLanguage();

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const toggleMonochrome = () => {
        setMonochrome(!monochrome);
        document.documentElement.classList.toggle('monochrome');
    };

    const isActive = (path: string) => location.pathname === path ? 'text-primary' : 'hover:text-primary';

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 px-6 py-4 ${scrolled ? 'bg-white/90 dark:bg-slate-900/90 backdrop-blur-lg shadow-xl py-3' : 'bg-transparent'
            }`}>
            <div className="max-w-7xl mx-auto flex justify-between items-center">
                <Link to="/" className="text-3xl font-black tracking-tighter text-primary group cursor-pointer">
                    WORLD<span className="text-secondary group-hover:text-primary transition-colors">TOUR</span>
                </Link>

                <div className="hidden md:flex items-center gap-8 font-medium">
                    <Link to="/" className={`${isActive('/')} transition-colors`}>{t('nav.destinations')}</Link>
                    <Link to="/hotels" className={`${isActive('/hotels')} transition-colors`}>{t('nav.hotels')}</Link>
                    <Link to="/flights" className={`${isActive('/flights')} transition-colors`}>{t('nav.flights')}</Link>
                    <Link to="/ai-assistant" className={`${isActive('/ai-assistant')} transition-colors`}>{t('nav.ai_assistant')}</Link>
                </div>

                <div className="flex items-center gap-4">
                    {/* B&W Toggle */}
                    <button
                        onClick={toggleMonochrome}
                        className={`p-2 rounded-full transition-all ${monochrome ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-800'}`}
                        title="Toggle Black & White Theme"
                    >
                        <Palette className="w-5 h-5" />
                    </button>

                    {/* Language Selector */}
                    <div className="flex gap-2 bg-white/50 backdrop-blur-sm p-1 rounded-full border border-slate-200 overflow-x-auto max-w-[200px] scrollbar-hide">
                        <button onClick={() => setLanguage('en')} className={`text-xl p-1 rounded-full transition-transform ${language === 'en' ? 'scale-125 shadow-md bg-white' : 'opacity-50 hover:opacity-100'}`} title="English">🇬🇧</button>
                        <button onClick={() => setLanguage('fr')} className={`text-xl p-1 rounded-full transition-transform ${language === 'fr' ? 'scale-125 shadow-md bg-white' : 'opacity-50 hover:opacity-100'}`} title="Français">🇫🇷</button>
                        <button onClick={() => setLanguage('es')} className={`text-xl p-1 rounded-full transition-transform ${language === 'es' ? 'scale-125 shadow-md bg-white' : 'opacity-50 hover:opacity-100'}`} title="Español">🇪🇸</button>
                        <button onClick={() => setLanguage('zh')} className={`text-xl p-1 rounded-full transition-transform ${language === 'zh' ? 'scale-125 shadow-md bg-white' : 'opacity-50 hover:opacity-100'}`} title="中文">🇨🇳</button>
                        <button onClick={() => setLanguage('ar')} className={`text-xl p-1 rounded-full transition-transform ${language === 'ar' ? 'scale-125 shadow-md bg-white' : 'opacity-50 hover:opacity-100'}`} title="العربية">🇸🇦</button>
                        <button onClick={() => setLanguage('sw')} className={`text-xl p-1 rounded-full transition-transform ${language === 'sw' ? 'scale-125 shadow-md bg-white' : 'opacity-50 hover:opacity-100'}`} title="Kiswahili">🇰🇪</button>
                    </div>

                    <CurrencySelector />

                    {isAuthenticated ? (
                        <>
                            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary font-bold">
                                <UserIcon className="w-4 h-4" />
                                <span>{user?.username}</span>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="px-4 py-2.5 rounded-full font-bold border-2 border-red-500/20 hover:border-red-500 text-red-600 dark:text-red-400 transition-all flex items-center gap-2"
                            >
                                <LogOut className="w-4 h-4" />
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="px-6 py-2.5 rounded-full font-bold border-2 border-primary/20 hover:border-primary transition-all text-center">
                                {t('nav.login')}
                            </Link>
                            <Link to="/signup" className="px-6 py-2.5 rounded-full font-bold bg-primary text-white shadow-lg shadow-primary/30 hover:shadow-primary/50 transition-all active:scale-95 text-center">
                                Sign Up
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Nav;
