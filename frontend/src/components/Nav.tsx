import { useState, useEffect } from 'react';
import type { FC } from 'react';

const Nav: FC = () => {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 px-6 py-4 ${scrolled ? 'bg-white/80 dark:bg-slate-900/80 backdrop-blur-lg shadow-xl py-3' : 'bg-transparent'
            }`}>
            <div className="max-w-7xl mx-auto flex justify-between items-center">
                <div className="text-3xl font-black tracking-tighter text-primary group cursor-pointer">
                    WORLD<span className="text-secondary group-hover:text-primary transition-colors">TOUR</span>
                </div>

                <div className="hidden md:flex items-center gap-8 font-medium">
                    <a href="#" className="hover:text-primary transition-colors">Destinations</a>
                    <a href="#" className="hover:text-primary transition-colors">Hotels</a>
                    <a href="#" className="hover:text-primary transition-colors">Flights</a>
                    <a href="#" className="hover:text-primary transition-colors">AI Assistant</a>
                </div>

                <div className="flex items-center gap-4">
                    <button className="px-6 py-2.5 rounded-full font-bold border-2 border-primary/20 hover:border-primary transition-all">
                        Login
                    </button>
                    <button className="px-6 py-2.5 rounded-full font-bold bg-primary text-white shadow-lg shadow-primary/30 hover:shadow-primary/50 transition-all active:scale-95">
                        Sign Up
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Nav;
