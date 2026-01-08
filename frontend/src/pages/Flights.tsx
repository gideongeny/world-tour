import { useState, useEffect } from 'react';
import { Plane, Calendar, ArrowRight, Clock } from 'lucide-react';

interface Flight {
    id: number;
    airline: string;
    origin: string;
    destination: string;
    price: number;
    departure: string; // Time or Date
    duration: string;
}

function Flights() {
    const [flights, setFlights] = useState<Flight[]>([]);
    const [loading, setLoading] = useState(true);
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');
    const [date, setDate] = useState('');

    useEffect(() => {
        fetch('/booking/flights?format=json')
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) setFlights(data);
                else setFlights([
                    { id: 1, airline: 'Emirates', origin: 'New York (JFK)', destination: 'Dubai (DXB)', price: 850, departure: '10:00 AM', duration: '12h 45m' },
                    { id: 2, airline: 'British Airways', origin: 'London (LHR)', destination: 'New York (JFK)', price: 620, departure: '02:30 PM', duration: '8h 15m' },
                ]);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, []);

    const handleSearch = () => {
        if (!origin.trim() || !destination.trim()) return;

        const params = new URLSearchParams({
            origin,
            dest: destination,
            date: date || new Date().toISOString().split('T')[0]
        });

        fetch(`/booking/external/flights/search?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                if (data.url) {
                    window.open(data.url, '_blank');
                }
            })
            .catch(err => console.error("Flight search failed:", err));
    };

    const handleBook = (flightId: number) => {
        alert(`Flight ${flightId} selected! Redirecting to payment...`);
    };

    return (
        <div className="pt-24 pb-20 px-6 max-w-5xl mx-auto min-h-screen">
            <div className="mb-12">
                <h1 className="text-5xl font-black mb-4 tracking-tight">Search Flights</h1>
                <p className="text-xl text-slate-500">Find the best deals on air travel worldwide.</p>
            </div>

            {/* Search Widget */}
            <div className="bg-white dark:bg-slate-800 p-6 rounded-3xl shadow-xl mb-12 border border-slate-100 dark:border-slate-700">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-xl">
                        <label className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                            <Plane className="w-3 h-3" /> From
                        </label>
                        <input
                            type="text"
                            placeholder="Origin City"
                            value={origin}
                            onChange={(e) => setOrigin(e.target.value)}
                            className="w-full bg-transparent font-bold outline-none"
                        />
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-xl">
                        <label className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                            <Plane className="w-3 h-3 rotate-90" /> To
                        </label>
                        <input
                            type="text"
                            placeholder="Destination City"
                            value={destination}
                            onChange={(e) => setDestination(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                            className="w-full bg-transparent font-bold outline-none"
                        />
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-xl">
                        <label className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                            <Calendar className="w-3 h-3" /> Departure
                        </label>
                        <input
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full bg-transparent font-bold outline-none"
                        />
                    </div>
                    <button
                        onClick={handleSearch}
                        className="bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/30 hover:bg-primary/90 transition-all flex items-center justify-center gap-2"
                    >
                        Search Flights
                    </button>
                </div>
            </div>

            <div className="space-y-4">
                {flights.map(flight => (
                    <div key={flight.id} className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 hover:shadow-md transition-all flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="flex items-center gap-4 flex-1">
                            <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center font-bold text-slate-500">
                                {flight.airline[0]}
                            </div>
                            <div>
                                <h3 className="font-bold text-lg">{flight.airline}</h3>
                                <div className="flex items-center gap-2 text-slate-500 text-sm">
                                    <span className="bg-slate-100 px-2 py-0.5 rounded text-xs">Economy</span>
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-1 items-center justify-center gap-6">
                            <div className="text-right">
                                <div className="text-2xl font-black">{flight.departure}</div>
                                <div className="text-slate-500 font-bold">{flight.origin.split('(')[1]?.replace(')', '') || flight.origin}</div>
                            </div>
                            <div className="flex flex-col items-center gap-1 w-24">
                                <span className="text-xs text-slate-400 flex items-center gap-1"><Clock className="w-3 h-3" /> {flight.duration}</span>
                                <div className="h-0.5 w-full bg-slate-200 relative">
                                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-200 p-1 rounded-full">
                                        <Plane className="w-3 h-3 text-slate-400 rotate-90" />
                                    </div>
                                </div>
                                <span className="text-xs text-primary font-bold">Non-stop</span>
                            </div>
                            <div>
                                <div className="text-2xl font-black text-slate-400">--:--</div>
                                <div className="text-slate-500 font-bold">{flight.destination.split('(')[1]?.replace(')', '') || flight.destination}</div>
                            </div>
                        </div>

                        <div className="w-full md:w-auto text-right">
                            <div className="text-3xl font-black text-slate-900 dark:text-white mb-2">${flight.price}</div>
                            <button
                                onClick={() => handleBook(flight.id)}
                                className="w-full px-6 py-3 bg-slate-900 dark:bg-white dark:text-slate-900 text-white rounded-xl font-bold hover:opacity-90 transition-opacity">
                                Select Flight
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Flights;
