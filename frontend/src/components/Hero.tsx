import type { FC } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Phone } from 'lucide-react';

const Hero: FC = () => {
    return (
        <div className="relative h-[80vh] flex items-center justify-center overflow-hidden rounded-3xl mb-12">
            <div className="absolute inset-0 z-0">
                <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/60 z-10" />
                <img
                    src="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&q=80"
                    className="w-full h-full object-cover transform scale-105 hover:scale-100 transition-transform duration-1000"
                    alt="World Tour"
                />
            </div>

            <div className="relative z-20 text-center px-6 max-w-4xl">
                <h1 className="text-6xl md:text-8xl font-black text-white mb-6 drop-shadow-2xl">
                    Explore the <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">World</span>
                </h1>
                <p className="text-xl text-white/90 mb-10 max-w-2xl mx-auto drop-shadow-lg">
                    Discover hand-picked destinations, personalized itineraries, and elite experiences curated just for you.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
                    <Link
                        to="/signup"
                        className="px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2"
                    >
                        Get Started
                        <ArrowRight className="w-5 h-5" />
                    </Link>
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
