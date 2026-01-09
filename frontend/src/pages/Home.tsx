import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Hero from '../components/Hero'
import Monetag from '../components/Monetag'
import DestinationCard from '../components/DestinationCard'
import Map from '../components/Map'
import PageTransition from '../components/PageTransition'
import { useLanguage } from '../context/LanguageContext'

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
}

function Home() {
    const [destinations, setDestinations] = useState<Destination[]>([]);
    const [loading, setLoading] = useState(true);
    const { t } = useLanguage();

    useEffect(() => {
        fetch('/booking/destinations?format=json')
            .then((res: Response) => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            })
            .then((data: any) => {
                if (Array.isArray(data)) {
                    setDestinations(data);
                } else if (data && typeof data === 'object' && Array.isArray(data.destinations)) {
                    setDestinations(data.destinations);
                } else {
                    console.error("Data is not an array:", data);
                    setDestinations([]);
                }
                setLoading(false);
            })
            .catch((err: Error) => {
                console.error("Failed to fetch destinations:", err);
                setDestinations([]);
                setLoading(false);
            });
    }, []);

    const mapMarkers = destinations.map(d => ({
        lat: d.latitude || 0,
        lng: d.longitude || 0,
        title: d.name,
        description: `Starting from $${d.price}`
    }));

    return (
        <PageTransition>
            <div className="pt-24 pb-20 px-6 max-w-7xl mx-auto">
                <Hero />
                <Monetag />

                <section id="destinations" className="mb-20">
                    <div className="flex justify-between items-end mb-8">
                        <div>
                            <h2 className="text-4xl font-black mb-2 tracking-tight font-serif">{t('home.destinations.title')}</h2>
                            <p className="text-slate-500 dark:text-slate-400">{t('hero.subtitle')}</p>
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

                <section id="map" className="mb-20">
                    <div className="mb-8">
                        <h2 className="text-4xl font-black mb-2 tracking-tight font-serif">{t('home.map.title')}</h2>
                        <p className="text-slate-500 dark:text-slate-400">{t('hero.subtitle')}</p>
                    </div>
                    <Map markers={mapMarkers} center={[20, 10]} zoom={2} />
                </section>

                <section className="relative rounded-3xl overflow-hidden py-24 px-12 text-center text-white">
                    <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary z-10 opacity-90" />
                    <div className="absolute inset-0 z-0">
                        <img src="https://images.unsplash.com/photo-1488085061387-422e29b40080?auto=format&fit=crop&q=80" className="w-full h-full object-cover" alt="CTA" />
                    </div>
                    <div className="relative z-20 max-w-2xl mx-auto">
                        <h2 className="text-5xl font-black mb-6 drop-shadow-lg font-serif">{t('home.cta.title')}</h2>
                        <p className="text-xl mb-10 text-white/90">{t('hero.subtitle')}</p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link to="/hotels" className="px-10 py-4 bg-white text-slate-900 rounded-2xl font-black shadow-2xl hover:bg-slate-50 transition-colors inline-block">
                                {t('common.get_started')}
                            </Link>
                            <Link to="/contact" className="px-10 py-4 bg-white/20 backdrop-blur-md rounded-2xl font-black border border-white/30 hover:bg-white/30 transition-colors inline-block">
                                {t('common.contact_sales')}
                            </Link>
                        </div>
                    </div>
                </section>
            </div>
        </PageTransition>
    )
}

export default Home
