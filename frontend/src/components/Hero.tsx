import { FC, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Phone, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

const BACKGROUND_IMAGES = [
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&q=80", // Tropical
    "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&q=80", // Safari
    "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&q=80", // Santorini
    "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&q=80", // Kyoto
    "https://images.unsplash.com/photo-1546412414-e1885259563a?auto=format&fit=crop&q=80"  // Dubai
];

const Firefly = ({ delay }: { delay: number }) => (
    <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{
            opacity: [0, 1, 0],
            scale: [0, 1.5, 0],
            x: [0, Math.random() * 100 - 50, Math.random() * 100 - 50],
            y: [0, Math.random() * -100 - 50, Math.random() * -100 - 100],
        }}
        transition={{
            duration: 5 + Math.random() * 5,
            repeat: Infinity,
            delay: delay,
            ease: "easeInOut"
        }}
        className="absolute w-2 h-2 bg-yellow-400 rounded-full blur-[1px] shadow-[0_0_10px_rgba(250,204,21,0.8)] z-20 pointer-events-none"
        style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
        }}
    />
);

const Hero: FC = () => {
    const [currentIndex, setCurrentIndex] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentIndex((prev) => (prev + 1) % BACKGROUND_IMAGES.length);
        }, 5000);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="relative h-[80vh] flex items-center justify-center overflow-hidden rounded-3xl mb-12">
            <div className="absolute inset-0 z-0">
                <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/60 z-10" />
                {BACKGROUND_IMAGES.map((img, idx) => (
                    <img
                        key={img}
                        src={img}
                        className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 animate-ken-burns ${idx === currentIndex ? 'opacity-100' : 'opacity-0'
                            }`}
                        alt="Destinations"
                    />
                ))}
            </div>

            {/* Fireflies Atmosphere */}
            {[...Array(20)].map((_, i) => <Firefly key={i} delay={i * 0.5} />)}

            <div className="relative z-20 text-center px-6 max-w-4xl">
                <motion.h1
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1, type: "spring", bounce: 0.5 }}
                    className="text-6xl md:text-8xl font-black text-white mb-6 drop-shadow-2xl font-serif"
                >
                    Explore the <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-400">World</span>
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5, duration: 1 }}
                    className="text-xl text-white/90 mb-10 max-w-2xl mx-auto drop-shadow-lg"
                >
                    Discover hand-picked destinations, personalized itineraries, and elite experiences curated just for you.
                </motion.p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
                    <Link
                        to="/signup"
                        className="px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2"
                    >
                        Get Started
                        <ArrowRight className="w-5 h-5" />
                    </Link>

                    <a
                        href="https://otieu.com/4/10436633"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-8 py-4 bg-amber-500 hover:bg-amber-600 text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2 animate-pulse"
                    >
                        <Sparkles className="w-5 h-5" />
                        Secret Deals
                    </a>

                    <Link
                        to="/contact"
                        className="px-8 py-4 bg-white/10 backdrop-blur-sm text-white border-2 border-white/30 rounded-xl font-bold hover:bg-white/20 transition-all flex items-center justify-center gap-2"
                    >
                        <Phone className="w-5 h-5" />
                        Contact Sales
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Hero;
