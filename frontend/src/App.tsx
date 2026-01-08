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
