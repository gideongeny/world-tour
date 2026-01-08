import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Nav: FC = () => {
    const [scrolled, setScrolled] = useState(false);
    const location = useLocation();

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const isActive = (path: string) => location.pathname === path ? 'text-primary' : 'hover:text-primary';

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 px-6 py-4 ${scrolled ? 'bg-white/90 dark:bg-slate-900/90 backdrop-blur-lg shadow-xl py-3' : 'bg-transparent'
            }`}>
            <div className="max-w-7xl mx-auto flex justify-between items-center">
                <Link to="/" className="text-3xl font-black tracking-tighter text-primary group cursor-pointer">
                    WORLD<span className="text-secondary group-hover:text-primary transition-colors">TOUR</span>
                </Link>

                <div className="hidden md:flex items-center gap-8 font-medium">
                    <Link to="/" className={`${isActive('/')} transition-colors`}>Destinations</Link>
                    <Link to="/hotels" className={`${isActive('/hotels')} transition-colors`}>Hotels</Link>
                    <Link to="/flights" className={`${isActive('/flights')} transition-colors`}>Flights</Link>
                    <Link to="/ai-assistant" className={`${isActive('/ai-assistant')} transition-colors`}>AI Assistant</Link>
                </div>

                <div className="flex items-center gap-4">
                    <Link to="/login" className="px-6 py-2.5 rounded-full font-bold border-2 border-primary/20 hover:border-primary transition-all text-center">
                        Login
                    </Link>
                    <Link to="/signup" className="px-6 py-2.5 rounded-full font-bold bg-primary text-white shadow-lg shadow-primary/30 hover:shadow-primary/50 transition-all active:scale-95 text-center">
                        Sign Up
                    </Link>
                </div>
            </div>
        </nav>
    );
};

export default Nav;
