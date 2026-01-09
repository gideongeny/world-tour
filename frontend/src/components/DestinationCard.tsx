import { useNavigate } from 'react-router-dom';
import Tilt from 'react-parallax-tilt';
import Price from './Price';
import { Sparkles, Heart } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { useState } from 'react';

interface Destination {
    id: number;
    name: string;
    country: string;
    image_url: string;
    price: number;
    rating: number;
    category: string;
    quote?: string;
}

const DestinationCard: React.FC<{ destination: Destination }> = ({ destination }) => {
    const navigate = useNavigate();
    const { isAuthenticated } = useUser();
    const [isSaved, setIsSaved] = useState(false);

    const handleSave = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (!isAuthenticated) return alert('Please login to save trips!');

        try {
            const res = await fetch('/api/user/wishlist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    type: 'destination',
                    data: {
                        id: destination.id,
                        name: destination.name,
                        price: destination.price,
                        image_url: destination.image_url,
                        country: destination.country
                    }
                })
            });
            if (res.ok) {
                setIsSaved(true);
            }
        } catch (error) {
            console.error('Failed to save', error);
        }
    };

    const handleBook = () => {
        const params = new URLSearchParams({
            type: 'Destination',
            name: destination.name,
            price: destination.price.toString(),
            image: destination.image_url
        });
        navigate(`/checkout?${params.toString()}`);
    };

    return (
        <Tilt
            tiltMaxAngleX={5}
            tiltMaxAngleY={5}
            scale={1.02}
            transitionSpeed={2000}
            className="h-[450px] w-full perspective-1000 group"
            glareEnable={false}
        >
            <div className="relative w-full h-full text-left transition-transform duration-[800ms] ease-in-out transform-style-3d group-hover:rotate-y-180 group-hover:delay-[7000ms] delay-0 shadow-xl rounded-2xl">

                {/* Front Face (Image) */}
                <div className="absolute inset-0 backface-hidden rounded-2xl overflow-hidden glass-card">
                    <div className="relative h-64 overflow-hidden">
                        <img
                            src={destination.image_url || 'https://images.unsplash.com/photo-1488085061387-422e29b40080?auto=format&fit=crop&q=80'}
                            alt={destination.name}
                            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                            onError={(e) => {
                                const target = e.target as HTMLImageElement;
                                target.src = 'https://images.unsplash.com/photo-1488085061387-422e29b40080?auto=format&fit=crop&q=80';
                            }}
                        />
                        <div className="absolute top-4 right-4 bg-white/90 dark:bg-slate-800/90 px-3 py-1 rounded-full text-sm font-bold shadow-lg backdrop-blur-md">
                            <Price amount={destination.price} />
                        </div>
                        <button
                            onClick={handleSave}
                            className="absolute top-4 left-4 p-2 bg-white/90 dark:bg-slate-800/90 rounded-full shadow-lg backdrop-blur-md hover:scale-110 transition-transform group/heart"
                        >
                            <Heart className={`w-5 h-5 ${isSaved ? 'fill-red-500 text-red-500' : 'text-slate-400 group-hover/heart:text-red-500'} transition-colors`} />
                        </button>
                    </div>
                    <div className="p-6">
                        <div className="flex justify-between items-start mb-2">
                            <div>
                                <h3 className="text-xl font-bold font-serif text-primary dark:text-orange-400">{destination.name}</h3>
                                <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">{destination.country}</p>
                            </div>
                            <div className="flex items-center text-amber-500 bg-amber-100 dark:bg-amber-900/30 px-2 py-1 rounded-lg">
                                <span className="mr-1 font-bold">{destination.rating}</span>
                                <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                            </div>
                        </div>
                        <div className="mt-4 flex gap-2">
                            <span className="px-3 py-1 bg-primary/10 text-primary text-xs rounded-full uppercase font-bold tracking-wider">
                                {destination.category}
                            </span>
                        </div>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                handleBook();
                            }}
                            className="w-full mt-4 py-3 bg-gradient-to-r from-primary to-secondary text-white rounded-xl font-bold shadow-lg hover:shadow-primary/50 transition-all duration-300 transform hover:-translate-y-1 relative z-20"
                        >
                            Book Experience
                        </button>
                    </div>
                </div>

                {/* Back Face (Quote) */}
                <div className="absolute inset-0 backface-hidden rounded-2xl overflow-hidden glass-card bg-gradient-to-br from-primary/95 to-secondary/95 p-8 flex flex-col items-center justify-center text-center rotate-y-180">
                    <Sparkles className="w-12 h-12 text-yellow-300 mb-6 animate-pulse" />
                    <blockquote className="text-xl font-serif italic text-white mb-8 border-l-4 border-yellow-400 pl-4">
                        "{destination.quote || "Experience the magic of this destination."}"
                    </blockquote>
                    <button
                        onClick={handleBook}
                        className="w-full mt-auto py-3 bg-white text-primary rounded-xl font-bold shadow-lg hover:bg-slate-50 transition-all duration-300 transform hover:scale-105"
                    >
                        Book Experience
                    </button>
                </div>

            </div>
        </Tilt>
    );
};

export default DestinationCard;
