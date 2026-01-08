import type { FC } from 'react';

interface Destination {
    id: number;
    name: string;
    country: string;
    image_url: string;
    price: number;
    rating: number;
    category: string;
}

const DestinationCard: FC<{ destination: Destination }> = ({ destination }) => {
    return (
        <div className="glass-card rounded-2xl overflow-hidden group hover:scale-105 transition-all duration-300">
            <div className="relative h-64 overflow-hidden">
                <img
                    src={destination.image_url || 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800'}
                    alt={destination.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute top-4 right-4 bg-white/90 dark:bg-slate-800/90 px-3 py-1 rounded-full text-sm font-bold shadow-lg">
                    ${destination.price}
                </div>
            </div>
            <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                    <div>
                        <h3 className="text-xl font-bold">{destination.name}</h3>
                        <p className="text-sm text-slate-500 dark:text-slate-400">{destination.country}</p>
                    </div>
                    <div className="flex items-center text-amber-500">
                        <span className="mr-1">{destination.rating}</span>
                        <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                    </div>
                </div>
                <div className="mt-4 flex gap-2">
                    <span className="px-3 py-1 bg-primary/10 text-primary text-xs rounded-full uppercase font-bold">
                        {destination.category}
                    </span>
                </div>
                <button className="w-full mt-6 py-3 bg-gradient-to-r from-primary to-secondary text-white rounded-xl font-bold shadow-lg hover:shadow-primary/50 transition-all duration-300">
                    Book Now
                </button>
            </div>
        </div>
    );
};

export default DestinationCard;
