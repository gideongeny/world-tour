import { Palette, LogOut, User as UserIcon, Globe, ChevronDown } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import CurrencySelector from './CurrencySelector';

const Nav: FC = () => {
    const [scrolled, setScrolled] = useState(false);
    const [monochrome, setMonochrome] = useState(false);
    const [langOpen, setLangOpen] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout, isAuthenticated } = useUser();
    const { language, setLanguage, t } = useLanguage();

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

                    {/* Pro Language Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setLangOpen(!langOpen)}
                            className="flex items-center gap-2 bg-white/50 backdrop-blur-sm px-3 py-2 rounded-full border border-slate-200 hover:bg-white transition-all font-medium text-sm min-w-[100px]"
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
