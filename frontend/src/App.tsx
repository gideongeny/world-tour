import { useState, useEffect } from 'react'
import Nav from './components/Nav'
import Hero from './components/Hero'
import DestinationCard from './components/DestinationCard'
import Map from './components/Map'


interface Destination {
  id: number;
  name: string;
  country: string;
  image_url: string;
  price: number;
  rating: number;
  category: string;
}


function App() {
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    fetch('https://world-tour-backend.vercel.app/booking/destinations?format=json')
      .then((res: Response) => res.json())
      .then((data: Destination[]) => {
        setDestinations(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        console.error("Failed to fetch destinations:", err);
        setLoading(false);
      });
  }, []);


  const mapMarkers = destinations.map(d => ({
    // Use fallback coordinates if none provided
    lat: (d as any).latitude || 0,
    lng: (d as any).longitude || 0,
    title: d.name,
    description: `Starting from $${d.price}`
  }));

  return (
    <div className="min-h-screen bg-background">
      <Nav />

      <main className="max-w-7xl mx-auto px-6 pt-24 pb-20">
        <Hero />

        <section className="mb-20">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h2 className="text-4xl font-black mb-2 tracking-tight">World Class Destinations</h2>
              <p className="text-slate-500 dark:text-slate-400">Hand-picked by our experts for your next adventure</p>
            </div>
            <button className="text-primary font-bold hover:underline">View All</button>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-96 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-2xl" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {destinations.map(destination => (
                <DestinationCard key={destination.id} destination={destination} />
              ))}
            </div>
          )}
        </section>

        <section className="mb-20">
          <div className="mb-8">
            <h2 className="text-4xl font-black mb-2 tracking-tight">Explore the Map</h2>
            <p className="text-slate-500 dark:text-slate-400">Visualise your next journey across the globe</p>
          </div>
          <Map markers={mapMarkers} center={[20, 10]} zoom={2} />
        </section>

        <section className="relative rounded-3xl overflow-hidden py-24 px-12 text-center text-white">
          <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary z-0 opacity-90" />
          <div className="absolute inset-0 z-[-1]">
            <img src="https://images.unsplash.com/photo-1488085061387-422e29b40080?auto=format&fit=crop&q=80" className="w-full h-full object-cover" alt="CTA" />
          </div>
          <div className="relative z-10 max-w-2xl mx-auto">
            <h2 className="text-5xl font-black mb-6 drop-shadow-lg">Ready for your next adventure?</h2>
            <p className="text-xl mb-10 text-white/90">Join 50k+ happy travelers and start booking your dream trip today.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-10 py-4 bg-white text-slate-900 rounded-2xl font-black shadow-2xl hover:bg-slate-50 transition-colors">
                Get Started
              </button>
              <button className="px-10 py-4 bg-white/20 backdrop-blur-md rounded-2xl font-black border border-white/30 hover:bg-white/30 transition-colors">
                Contact Sales
              </button>
            </div>
          </div>
        </section>
      </main>

      <footer className="py-12 px-6 border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8 text-slate-500 dark:text-slate-400">
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            WORLD<span className="text-primary">TOUR</span>
          </div>
          <p>© 2026 World Tour. All rights reserved.</p>
          <div className="flex gap-8">
            <a href="#" className="hover:text-primary transition-colors">Privacy</a>
            <a href="#" className="hover:text-primary transition-colors">Terms</a>
            <a href="#" className="hover:text-primary transition-colors">Cookies</a>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
