import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Star, MapPin, Wifi, Coffee, Globe } from 'lucide-react';
import { useCurrency } from '../context/CurrencyContext';

interface Hotel {
    id: number;
    name: string;
    location: string; // or country/city
    price: number;
    rating: number;
    image_url: string;
    description?: string;
}

const HotelCard = ({ hotel, onBook }: { hotel: Hotel, onBook: (h: Hotel) => void }) => {
    const { formatPrice } = useCurrency();
    return (
        <div className="group bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
            <div className="relative h-64 overflow-hidden">
                <img
                    src={hotel.image_url}
                    alt={hotel.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div className="absolute top-4 right-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-3 py-1 rounded-full text-sm font-bold shadow-sm flex items-center gap-1">
                    <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                    {hotel.rating}
                </div>
            </div>
            <div className="p-6">
                <div className="flex items-start justify-between mb-2">
                    <div>
                        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-1 group-hover:text-primary transition-colors">{hotel.name}</h3>
                        <div className="flex items-center gap-1 text-slate-500 text-sm">
                            <MapPin className="w-4 h-4" />
                            {hotel.location}
                        </div>
                    </div>
                </div>

                <p className="text-slate-600 dark:text-slate-400 text-sm line-clamp-2 mb-4">
                    {hotel.description || "Luxury accommodation with stunning views and world-class amenities."}
                </p>

                <div className="flex gap-3 mb-6">
                    <div className="p-2 bg-slate-50 dark:bg-slate-700 rounded-lg" title="Free Wifi"><Wifi className="w-4 h-4 text-slate-400" /></div>
                    <div className="p-2 bg-slate-50 dark:bg-slate-700 rounded-lg" title="Breakfast Included"><Coffee className="w-4 h-4 text-slate-400" /></div>
                    <div className="p-2 bg-slate-50 dark:bg-slate-700 rounded-lg" title="Central Location"><Globe className="w-4 h-4 text-slate-400" /></div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-700">
                    <div>
                        <span className="text-lg font-black text-primary">{formatPrice(hotel.price)}</span>
                        <span className="text-slate-400 text-sm">/night</span>
                    </div>
                    <button
                        onClick={() => onBook(hotel)}
                        className="px-4 py-2 bg-primary text-white rounded-xl font-bold text-sm shadow-lg shadow-primary/20 hover:bg-primary/90 transition-colors"
                    >
                        Book Now
                    </button>
                </div>
            </div>
        </div>
    );
};

function Hotels() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const query = searchParams.get('q');
    const [hotels, setHotels] = useState<Hotel[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const { currency, setCurrency, rates } = useCurrency();

    const [externalUrl, setExternalUrl] = useState<string | null>(null);

    const handleSearch = useCallback((overriddenQuery?: string) => {
        const activeQuery = overriddenQuery || searchQuery;
        if (!activeQuery.trim()) return;
        setLoading(true);
        setExternalUrl(null); // Reset external link

        // Fetch live results from LiteAPI via our backend
        fetch(`/booking/live/hotels/search?q=${encodeURIComponent(activeQuery)}`)
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data) && data.length > 0) {
                    setHotels(data);
                } else {
                    // Fallback: Get external URL but DO NOT auto-open (avoid popup blocker)
                    fetch(`/booking/external/hotels/search?q=${encodeURIComponent(activeQuery)}`)
                        .then(res => res.json())
                        .then(extData => {
                            if (extData.url) {
                                setExternalUrl(extData.url);
                                setHotels([]); // Clear previous hotels results to show fallback UI
                            }
                        });
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("LiteAPI search failed:", err);
                setLoading(false);
            });
    }, [searchQuery]);

    useEffect(() => {
        if (query) {
            setSearchQuery(query);
            handleSearch(query);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            fetch('/booking/hotels?format=json')
                .then(res => res.json())
                .then(data => {
                    if (Array.isArray(data)) setHotels(data);
                    else {
                        setHotels([
                            { id: 1, name: 'Grand Plaza', location: 'Paris, France', price: 350, rating: 4.8, image_url: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&q=80' },
                            { id: 2, name: 'Ocean View Resort', location: 'Bali, Indonesia', price: 220, rating: 4.9, image_url: 'https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&q=80' },
                        ]);
                    }
                    setLoading(false);
                })
                .catch(() => {
                    setLoading(false);
                });
        }
    }, [query, handleSearch]);

    const handleBook = (hotel: Hotel) => {
        const params = new URLSearchParams({
            type: 'Hotel',
            name: hotel.name,
            price: hotel.price.toString(),
            image: hotel.image_url
        });
        navigate(`/checkout?${params.toString()}`);
    };

    return (
        <div className="pt-24 pb-20 px-6 max-w-7xl mx-auto min-h-screen">
            <div className="mb-12 text-center">
                <h1 className="text-5xl font-black mb-4 tracking-tight">Luxury Stays</h1>
                <p className="text-xl text-slate-500 max-w-2xl mx-auto">Find the perfect accommodation for your journey. From boutique hotels to luxury resorts.</p>
            </div>

            <div className="bg-white dark:bg-slate-800 p-4 rounded-2xl shadow-xl max-w-5xl mx-auto -mt-6 mb-16 flex gap-4 overflow-hidden border border-slate-100 dark:border-slate-700">
                <div className="flex-1 px-4 py-2">
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Destination</label>
                    <input
                        type="text"
                        placeholder="Where are you going?"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        className="w-full bg-transparent font-bold outline-none text-slate-800 dark:text-white"
                    />
                </div>
                <div className="bg-slate-200 w-px my-1"></div>
                <div className="flex-1 px-4 py-2">
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Dates</label>
                    <input type="text" placeholder="Add dates (Optional)" className="w-full bg-transparent font-bold outline-none text-slate-800 dark:text-white" />
                </div>
                <div className="bg-slate-200 w-px my-1"></div>
                <div className="px-4 py-2">
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Currency</label>
                    <select
                        value={currency}
                        onChange={(e) => setCurrency(e.target.value)}
                        className="bg-transparent font-bold outline-none text-slate-800 dark:text-white cursor-pointer"
                    >
                        {Object.keys(rates).map(curr => (
                            <option key={curr} value={curr} className="bg-white dark:bg-slate-800">{curr}</option>
                        ))}
                    </select>
                </div>
                <button
                    onClick={handleSearch}
                    className="bg-primary text-white px-8 rounded-xl font-bold shadow-lg shadow-primary/30 hover:bg-primary/90 transition-all"
                >
                    Search
                </button>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {[1, 2, 3].map(i => <div key={i} className="h-96 bg-slate-100 rounded-2xl animate-pulse"></div>)}
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {hotels.length > 0 ? (
                        hotels.map(h => (
                            <HotelCard
                                key={h.id}
                                hotel={h}
                                onBook={handleBook}
                            />
                        ))
                    ) : externalUrl ? (
                        <div className="col-span-full flex flex-col items-center justify-center text-center p-12 bg-white dark:bg-slate-800 rounded-3xl border border-dashed border-slate-300 dark:border-slate-700">
                            <h3 className="text-2xl font-bold mb-4">No direct partners found for "{searchQuery}"</h3>
                            <p className="text-slate-500 mb-8 max-w-md">However, we found excellent options via our trusted partner network.</p>
                            <a
                                href={externalUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-8 py-4 bg-primary text-white rounded-xl font-bold shadow-xl hover:scale-105 transition-transform flex items-center gap-2"
                            >
                                View Hotels on Google
                                <Globe className="w-5 h-5" />
                            </a>
                        </div>
                    ) : (
                        <div className="col-span-full text-center py-12 text-slate-500">
                            Try searching for "Paris", "Bali", or "Dubai"
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default Hotels;
