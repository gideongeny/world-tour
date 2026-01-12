import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { Sun, Moon, LogOut, User as UserIcon, ChevronDown, Menu, X } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useCurrency } from '../context/CurrencyContext';

const Nav: React.FC = () => {
    const [scrolled, setScrolled] = useState(false);
    const [darkMode, setDarkMode] = useState(false);
    const [langOpen, setLangOpen] = useState(false);
    const [currencyOpen, setCurrencyOpen] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout, isAuthenticated } = useUser();
    const { language, setLanguage, t } = useLanguage();
    const { currency, setCurrency, rates } = useCurrency();

    const languages = [
        { code: 'en', flag: '🇬🇧', label: 'English' },
        { code: 'fr', flag: '🇫🇷', label: 'Français' },
        { code: 'es', flag: '🇪🇸', label: 'Español' },
        { code: 'zh', flag: '🇨🇳', label: '中文' },
        { code: 'ar', flag: '🇸🇦', label: 'العربية' },
        { code: 'sw', flag: '🇰🇪', label: 'Kiswahili' },
    ] as const;

    const currentLang = languages.find(l => l.code === language) || languages[0];

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
        document.documentElement.classList.toggle('dark');
        localStorage.setItem('darkMode', (!darkMode).toString());
    };

    useEffect(() => {
        const savedDarkMode = localStorage.getItem('darkMode') === 'true';
        setDarkMode(savedDarkMode);
        if (savedDarkMode) {
            document.documentElement.classList.add('dark');
        }
    }, []);

    const isActive = (path: string) => location.pathname === path ? 'text-primary' : 'hover:text-primary';

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 px-6 py-4 ${scrolled ? 'bg-white/90 dark:bg-slate-900/90 backdrop-blur-lg shadow-xl py-3' : 'bg-transparent'
            }`}>
            <div className="max-w-7xl mx-auto flex justify-between items-center">
                <Link to="/" className="text-3xl font-black tracking-tighter text-primary group cursor-pointer z-50">
                    WORLD<span className="text-secondary group-hover:text-primary transition-colors">TOUR</span>
                </Link>





                <div className="hidden md:flex items-center gap-8 font-medium">
                    <Link to="/" className={`${isActive('/')} transition-colors`}>{t('nav.destinations')}</Link>
                    <Link to="/hotels" className={`${isActive('/hotels')} transition-colors`}>{t('nav.hotels')}</Link>
                    <Link to="/flights" className={`${isActive('/flights')} transition-colors`}>{t('nav.flights')}</Link>
                    <Link to="/ai-assistant" className={`${isActive('/ai-assistant')} transition-colors`}>{t('nav.ai_assistant')}</Link>
                </div>

                <div className="hidden md:flex items-center gap-4">
                    {/* Dark/Light Mode Toggle */}
                    <button
                        onClick={toggleDarkMode}
                        className="p-2 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all"
                        title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
                    >
                        {darkMode ? <Sun className="w-5 h-5 text-yellow-500" /> : <Moon className="w-5 h-5 text-slate-700" />}
                    </button>

                    {/* Pro Language Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setLangOpen(!langOpen)}
                            className="flex items-center gap-2 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm px-3 py-2 rounded-full border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-800 transition-all font-medium text-sm min-w-[100px]"
                        >
                            <span className="text-lg">{currentLang.flag}</span>
                            <span>{currentLang.code.toUpperCase()}</span>
                            <ChevronDown className={`w-3 h-3 transition-transform ${langOpen ? 'rotate-180' : ''}`} />
                        </button>

                        {langOpen && (
                            <>
                                <div className="fixed inset-0 z-10" onClick={() => setLangOpen(false)} />
                                <div className="absolute top-full right-0 mt-2 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-100 dark:border-slate-800 p-2 min-w-[160px] flex flex-col gap-1 z-20 animate-in fade-in slide-in-from-top-2">
                                    {languages.map((l) => (
                                        <button
                                            key={l.code}
                                            onClick={() => {
                                                setLanguage(l.code as any);
                                                setLangOpen(false);
                                            }}
                                            className={`flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm font-medium ${language === l.code ? 'text-primary bg-primary/5' : 'text-slate-600 dark:text-slate-300'}`}
                                        >
                                            <span className="text-lg">{l.flag}</span>
                                            <span>{l.label}</span>
                                        </button>
                                    ))}
                                </div>
                            </>
                        )}
                    </div>

                    {/* Pro Currency Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setCurrencyOpen(!currencyOpen)}
                            className="flex items-center gap-2 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm px-3 py-2 rounded-full border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-800 transition-all font-medium text-sm min-w-[90px]"
                        >
                            <span className="font-bold">{currency}</span>
                            <ChevronDown className={`w-3 h-3 transition-transform ${currencyOpen ? 'rotate-180' : ''}`} />
                        </button>

                        {currencyOpen && (
                            <>
                                <div className="fixed inset-0 z-10" onClick={() => setCurrencyOpen(false)} />
                                <div className="absolute top-full right-0 mt-2 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-100 dark:border-slate-800 p-2 min-w-[120px] max-h-[300px] overflow-y-auto flex flex-col gap-1 z-20 animate-in fade-in slide-in-from-top-2">
                                    {Object.keys(rates).map((curr) => (
                                        <button
                                            key={curr}
                                            onClick={() => {
                                                setCurrency(curr);
                                                setCurrencyOpen(false);
                                            }}
                                            className={`flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm font-medium ${currency === curr ? 'text-primary bg-primary/5' : 'text-slate-600 dark:text-slate-300'}`}
                                        >
                                            <span>{curr}</span>
                                        </button>
                                    ))}
                                </div>
                            </>
                        )}
                    </div>


                    {isAuthenticated ? (
                        <>
                            <Link to="/profile" className="flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary font-bold hover:bg-primary/20 transition-all">
                                <UserIcon className="w-4 h-4" />
                                <span>{user?.username}</span>
                            </Link>
                            <button
                                onClick={handleLogout}
                                className="px-4 py-2.5 rounded-full font-bold border-2 border-red-500/20 hover:border-red-500 text-red-600 dark:text-red-400 transition-all flex items-center gap-2"
                            >
                                <LogOut className="w-4 h-4" />
                                {t('nav.logout')}
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="px-6 py-2.5 rounded-full font-bold border-2 border-primary/20 hover:border-primary transition-all text-center">
                                {t('nav.login')}
                            </Link>
                            <Link to="/signup" className="px-6 py-2.5 rounded-full font-bold bg-primary text-white shadow-lg shadow-primary/30 hover:shadow-primary/50 transition-all active:scale-95 text-center">
                                {t('nav.signup')}
                            </Link>
                        </>
                    )}


                </div>

                {/* Mobile Menu Toggle (RightAligned) */}
                <button
                    className="md:hidden ml-auto p-2 text-slate-800 dark:text-white z-50"
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                >
                    {mobileMenuOpen ? <X className="w-8 h-8" /> : <Menu className="w-8 h-8" />}
                </button>

                {/* Mobile Menu Overlay */}
                <div className={`fixed inset-0 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl z-40 flex flex-col items-center justify-center gap-8 transition-all duration-300 md:hidden ${mobileMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}>
                    <div className="flex flex-col gap-6 text-center text-2xl font-bold">
                        <Link to="/" onClick={() => setMobileMenuOpen(false)} className={`${isActive('/')}`}>{t('nav.destinations')}</Link>
                        <Link to="/hotels" onClick={() => setMobileMenuOpen(false)} className={`${isActive('/hotels')}`}>{t('nav.hotels')}</Link>
                        <Link to="/flights" onClick={() => setMobileMenuOpen(false)} className={`${isActive('/flights')}`}>{t('nav.flights')}</Link>
                        <Link to="/ai-assistant" onClick={() => setMobileMenuOpen(false)} className={`${isActive('/ai-assistant')}`}>{t('nav.ai_assistant')}</Link>
                    </div>

                    <div className="flex flex-col gap-4 w-64 items-center">
                        {/* Mobile Settings Controls */}
                        <div className="flex items-center gap-4 mb-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 w-full justify-center">
                            <button
                                onClick={toggleDarkMode}
                                className="p-3 rounded-full bg-white dark:bg-slate-700 shadow-sm"
                            >
                                {darkMode ? <Sun className="w-5 h-5 text-yellow-500" /> : <Moon className="w-5 h-5 text-slate-700" />}
                            </button>
                            <button
                                onClick={() => setLangOpen(!langOpen)}
                                className="flex items-center gap-2 bg-white dark:bg-slate-700 px-4 py-2 rounded-full shadow-sm font-bold text-sm"
                            >
                                <span className="text-lg">{currentLang.flag}</span>
                                <span>{currentLang.code.toUpperCase()}</span>
                            </button>
                            <button
                                onClick={() => setCurrencyOpen(!currencyOpen)}
                                className="flex items-center gap-2 bg-white dark:bg-slate-700 px-4 py-2 rounded-full shadow-sm font-bold text-sm"
                            >
                                <span>{currency}</span>
                            </button>
                        </div>

                        {isAuthenticated ? (
                            <button
                                onClick={() => { handleLogout(); setMobileMenuOpen(false); }}
                                className="px-6 py-4 rounded-xl font-bold border-2 border-red-500/20 text-red-600 flex items-center justify-center gap-2 w-full"
                            >
                                <LogOut className="w-5 h-5" />
                                {t('nav.logout')}
                            </button>
                        ) : (
                            <div className="flex flex-col gap-3 w-full">
                                <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="px-6 py-4 rounded-xl font-bold border-2 border-slate-200 dark:border-slate-700 text-center w-full">
                                    {t('nav.login')}
                                </Link>
                                <Link to="/signup" onClick={() => setMobileMenuOpen(false)} className="px-6 py-4 rounded-xl font-bold bg-primary text-white text-center shadow-xl w-full">
                                    {t('nav.signup')}
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Nav;
