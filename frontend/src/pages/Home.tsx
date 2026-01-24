import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Hero from '../components/Hero'
import InfiniteGallery from '../components/blocks/3d-gallery-photography'
import ScrollExpandMedia from '../components/blocks/scroll-expansion-hero'

import DestinationCard from '../components/DestinationCard'
import Map from '../components/Map'
import PageTransition from '../components/PageTransition'
import { useLanguage } from '../context/LanguageContext'
import { API_BASE_URL } from '../config';

interface Destination {
    id: number;
    name: string;
    country: string;
    image_url: string;
    price: number;
    rating: number;
    category: string;
    latitude: number;
    longitude: number;
    description?: string; // Added description
}

const sampleImages = [
    { src: 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&auto=format&fit=crop&q=60', alt: 'Travel 1' },
    { src: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=600&auto=format&fit=crop&q=60', alt: 'Travel 2' },
    { src: 'https://images.unsplash.com/photo-1502791451862-7bd8c1df43a7?w=600&auto=format&fit=crop&q=60', alt: 'Travel 3' },
    { src: 'https://images.unsplash.com/photo-1530789253388-582c481c54b0?w=600&auto=format&fit=crop&q=60', alt: 'Travel 4' },
    { src: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600&auto=format&fit=crop&q=60', alt: 'Travel 5' },
    { src: 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=600&auto=format&fit=crop&q=60', alt: 'Travel 6' },
];


// Fallback destinations data for when backend is unavailable
const FALLBACK_DESTINATIONS: Destination[] = [
    { id: 1, name: 'Paris', country: 'France', image_url: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&q=80', price: 200, rating: 4.8, category: 'cultural', latitude: 48.8566, longitude: 2.3522 },
    { id: 2, name: 'Bali', country: 'Indonesia', image_url: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&q=80', price: 150, rating: 4.9, category: 'beach', latitude: -8.4095, longitude: 115.1889 },
    { id: 3, name: 'Maasai Mara', country: 'Kenya', image_url: '/assets/hero/maasai-mara-hero.jpg', price: 450, rating: 5.0, category: 'safari', latitude: -1.4061, longitude: 35.0839 },
    { id: 4, name: 'Zanzibar', country: 'Tanzania', image_url: '/assets/hero/zanzibar-hero.jpg', price: 280, rating: 4.8, category: 'beach', latitude: -6.1659, longitude: 39.2026 },
    { id: 5, name: 'Tokyo', country: 'Japan', image_url: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&q=80', price: 300, rating: 4.7, category: 'city', latitude: 35.6762, longitude: 139.6503 },
    { id: 6, name: 'New York', country: 'USA', image_url: 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&q=80', price: 280, rating: 4.6, category: 'city', latitude: 40.7128, longitude: -74.0060 },
    { id: 7, name: 'Maldives', country: 'Maldives', image_url: 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&q=80', price: 400, rating: 5.0, category: 'beach', latitude: 3.2028, longitude: 73.2207 },
    { id: 8, name: 'Dubai', country: 'UAE', image_url: 'https://images.unsplash.com/photo-1546412414-e1885259563a?auto=format&fit=crop&q=80', price: 350, rating: 4.5, category: 'luxury', latitude: 25.2048, longitude: 55.2708 },
    { id: 9, name: 'Santorini', country: 'Greece', image_url: 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&q=80', price: 250, rating: 4.9, category: 'luxury', latitude: 36.3932, longitude: 25.4615 },
    { id: 10, name: 'Shanghai', country: 'China', image_url: '/assets/hero/shanghai-hero.jpg', price: 280, rating: 4.7, category: 'city', latitude: 31.2304, longitude: 121.4737 },
    { id: 11, name: 'Sydney', country: 'Australia', image_url: 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&q=80', price: 350, rating: 4.9, category: 'beach', latitude: -33.8688, longitude: 151.2093 },
    { id: 12, name: 'Rio de Janeiro', country: 'Brazil', image_url: 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&q=80', price: 220, rating: 4.8, category: 'beach', latitude: -22.9068, longitude: -43.1729 },
];

function Home() {
    const [destinations, setDestinations] = useState<Destination[]>([]);
    const [loading, setLoading] = useState(true);
    const { t } = useLanguage();

    useEffect(() => {
        // Use a timeout to avoid hanging if backend is slow
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

        fetch(`${API_BASE_URL}/booking/destinations?format=json`, {
            signal: controller.signal,
        })
            .then((res: Response) => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            })
            .then((data: any) => {
                if (Array.isArray(data) && data.length > 0) {
                    setDestinations(data);
                } else if (data && typeof data === 'object' && Array.isArray(data.destinations) && data.destinations.length > 0) {
                    setDestinations(data.destinations);
                } else {
                    // Use fallback data
                    console.warn("Backend returned empty data, using fallback destinations");
                    setDestinations(FALLBACK_DESTINATIONS);
                }
                setLoading(false);
            })
            .catch((err: Error) => {
                console.warn("Failed to fetch destinations from backend, using fallback data:", err);
                // Use fallback data when backend is unavailable
                setDestinations(FALLBACK_DESTINATIONS);
                setLoading(false);
            })
            .finally(() => {
                clearTimeout(timeoutId);
            });
    }, []);

    const mapMarkers = destinations.map(d => ({
        lat: d.latitude || 0,
        lng: d.longitude || 0,
        title: d.name,
        description: `Starting from $${d.price}`
    }));

    // Use curated high-quality images for the Hero mainly to ensure the 3D effect works perfectly
    // and isn't dependent on user-generated content or potential broken links in the database.
    const heroImages = [
        { src: '/assets/hero/dakar-hero.jpg', alt: 'Dakar' }, // 1st
        { src: '/assets/hero/maasai-mara-hero.jpg', alt: 'Maasai Mara' }, // 2nd
        { src: '/assets/hero/shanghai-hero.jpg', alt: 'Shanghai' }, // 3rd
        { src: '/assets/hero/zanzibar-hero.jpg', alt: 'Zanzibar' }, // 4th
        // Fill remaining slots with trusted static images to keep the 3D effect full
        { src: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&q=80', alt: 'Paris' },
        { src: 'https://images.unsplash.com/photo-1546412414-e1885259563a?auto=format&fit=crop&q=80', alt: 'Dubai' },
        { src: 'https://images.unsplash.com/photo-1502791451862-7bd8c1df43a7?auto=format&fit=crop&q=80', alt: 'Tropical Beach' },
        { src: 'https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&q=80', alt: 'Safari' },
    ];

    const galleryImages = heroImages;

    return (
        <PageTransition>
            <div className="relative overflow-x-hidden">
                {/* 3D Gallery Hero */}
                {/* 3D Gallery Hero */}
                {/* 3D Gallery Hero */}
                <div className="relative h-[85vh] w-full overflow-hidden mb-0">
                    <InfiniteGallery
                        images={galleryImages}
                        speed={1.0}
                        zSpacing={2.5}
                        visibleCount={18}
                        className="h-full w-full"
                    />
                    <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/60 pointer-events-none z-[15]" />
                    <div className="absolute inset-0 pointer-events-none flex items-center justify-center z-20">
                        <div className="text-center px-6 max-w-4xl mx-auto">
                            <motion.h1
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="text-4xl sm:text-6xl md:text-8xl font-black text-white drop-shadow-[0_0_25px_rgba(0,0,0,0.7)] mb-4 md:mb-6 tracking-tight leading-tight"
                            >
                                Explore the World
                            </motion.h1>
                            <motion.p
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                                className="text-lg sm:text-xl md:text-2xl text-white font-medium drop-shadow-[0_2px_10px_rgba(0,0,0,0.8)] max-w-2xl mx-auto mb-8 md:mb-10 leading-relaxed px-4"
                            >
                                Discover your next adventure with World Tour.
                            </motion.p>
                            <div className="flex flex-col sm:flex-row gap-4 justify-center pointer-events-auto px-6">
                                <Link to="/signup" className="px-8 py-4 sm:px-10 sm:py-5 bg-white text-black rounded-full font-black text-base sm:text-lg hover:bg-slate-100 transition-all transform hover:scale-105 shadow-[0_0_30px_rgba(255,255,255,0.3)]">
                                    Start Journey
                                </Link>
                                <a href="#destinations" className="px-8 py-4 sm:px-10 sm:py-5 bg-black/30 backdrop-blur-md border-[1.5px] border-white/40 text-white rounded-full font-bold text-base sm:text-lg hover:bg-black/50 transition-all hover:border-white">
                                    View Destinations
                                </a>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="relative z-10 bg-background">
                    <div className="pt-24 pb-20 px-6 max-w-7xl mx-auto">


                        <section id="destinations" className="mb-20">
                            <div className="flex justify-between items-end mb-8">
                                <div>
                                    <h2 className="text-4xl font-black mb-2 tracking-tight font-serif">{t('home.destinations.title')}</h2>
                                    <p className="text-slate-500 dark:text-slate-400">{t('home.destinations.subtitle')}</p>
                                </div>
                                <Link to="/hotels" className="text-primary font-bold hover:underline">{t('common.view_all')}</Link>
                            </div>

                            {loading ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                                    {[1, 2, 3, 4].map(i => (
                                        <div key={i} className="h-96 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-2xl" />
                                    ))}
                                </div>
                            ) : (
                                <motion.div
                                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
                                    initial="hidden"
                                    animate="visible"
                                    variants={{
                                        hidden: { opacity: 0 },
                                        visible: {
                                            opacity: 1,
                                            transition: {
                                                staggerChildren: 0.1
                                            }
                                        }
                                    }}
                                >
                                    {destinations.map(destination => (
                                        <motion.div key={destination.id} variants={{
                                            hidden: { opacity: 0, y: 50 },
                                            visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100 } }
                                        }}>
                                            <DestinationCard destination={destination} />
                                        </motion.div>
                                    ))}
                                </motion.div>
                            )}
                        </section>

                    </div>

                    {/* Interactive Satellite Map - Full Width */}
                    <section className="mb-0 relative w-full h-[600px] overflow-hidden">
                        <div className="absolute top-10 left-6 z-10 pointer-events-none">
                            <h2 className="text-3xl font-black text-white drop-shadow-md flex items-center gap-3">
                                <span className="text-primary filter drop-shadow-lg">🌍</span> <span className="drop-shadow-lg">Global View</span>
                            </h2>
                        </div>
                        <Map
                            zoom={1.8}
                            className="h-full w-full rounded-none"
                            center={[20, 0]}
                            markers={destinations.map(d => ({
                                lat: d.latitude,
                                lng: d.longitude,
                                title: d.name,
                                description: d.country
                            }))}
                        />
                    </section>

                    {/* Full-Width Video Section with Centered Button */}
                    <section className="relative w-full h-[80vh] md:h-screen overflow-hidden">
                        {/* Video Background */}
                        <video
                            src="/assets/world-view.mp4"
                            autoPlay
                            muted
                            loop
                            playsInline
                            className="absolute inset-0 w-full h-full object-cover"
                        />

                        {/* Dark Overlay */}
                        <div className="absolute inset-0 bg-black/40" />

                        {/* Centered Content */}
                        <div className="absolute inset-0 flex items-center justify-center z-10">
                            <div className="text-center text-white px-6">
                                <motion.h2
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    className="text-4xl sm:text-6xl md:text-7xl font-black mb-4 md:mb-6 drop-shadow-[0_4px_20px_rgba(0,0,0,0.9)]"
                                >
                                    Unlock the Globe
                                </motion.h2>
                                <motion.p
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: 0.1 }}
                                    className="text-lg sm:text-xl md:text-2xl mb-8 md:mb-12 max-w-2xl mx-auto drop-shadow-[0_2px_10px_rgba(0,0,0,0.9)]"
                                >
                                    Get exclusive access to premium destinations worldwide
                                </motion.p>
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    whileInView={{ opacity: 1, scale: 1 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: 0.2 }}
                                >
                                    <Link
                                        to="/pricing"
                                        className="inline-block px-10 py-4 sm:px-16 sm:py-6 bg-white text-black rounded-full font-black text-lg sm:text-xl hover:bg-slate-100 transition-all transform hover:scale-110 shadow-[0_10px_40px_rgba(0,0,0,0.5)] hover:shadow-[0_15px_50px_rgba(0,0,0,0.6)]"
                                    >
                                        Join Premium
                                    </Link>
                                </motion.div>
                            </div>
                        </div>
                    </section>

                    <div className="pt-24 pb-20 px-0 max-w-full overflow-hidden bg-black text-white">
                        <div className="max-w-7xl mx-auto px-6 mb-12 text-center">
                            <h2 className="text-4xl font-black mb-4">World Tour Premium</h2>
                            <p className="text-xl text-gray-400 mb-8">Join thousands of travelers exploring the world's most exclusive locations.</p>
                            <Link to="/pricing" className="px-10 py-4 bg-primary text-white rounded-full font-bold shadow-2xl hover:bg-primary/90 transition-all transform hover:scale-105 inline-block">
                                Join Now - Start Your Journey
                            </Link>
                        </div>

                        {/* Auto Scrolling Marquee */}
                        <div className="relative flex overflow-x-hidden group">
                            <motion.div
                                className="flex gap-4 animate-marquee whitespace-nowrap"
                                animate={{ x: [0, -2000] }}
                                transition={{ repeat: Infinity, duration: 40, ease: "linear" }}
                            >
                                {[...destinations, ...destinations, ...destinations].map((dest, i) => (
                                    <div key={`${dest.id}-${i}`} className="w-80 h-56 rounded-xl overflow-hidden flex-shrink-0 relative">
                                        <img src={dest.image_url} alt={dest.name} className="w-full h-full object-cover" />
                                        <div className="absolute inset-0 bg-black/30 flex items-end p-4">
                                            <span className="font-bold text-white text-lg">{dest.name}</span>
                                        </div>
                                    </div>
                                ))}
                            </motion.div>
                        </div>

                        <style>{`
                            @keyframes marquee {
                                0% { transform: translateX(0); }
                                100% { transform: translateX(-50%); }
                            }
                        `}</style>
                    </div>
                </div>
            </div>
        </PageTransition>
    )
}

export default Home

