import type { FC } from 'react';

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
                <div className="glass-card p-2 rounded-2xl flex flex-col md:flex-row gap-2 max-w-3xl mx-auto border-white/30">
                    <input
                        type="text"
                        placeholder="Where do you want to go?"
                        className="flex-grow bg-white/10 text-white placeholder-white/60 border-none px-6 py-4 rounded-xl focus:ring-2 focus:ring-blue-400 outline-none"
                    />
                    <button className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-10 py-4 rounded-xl font-extrabold hover:shadow-2xl hover:shadow-blue-500/40 transition-all duration-300 transform active:scale-95">
                        Search
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Hero;
