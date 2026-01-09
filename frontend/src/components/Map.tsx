import { useEffect, useRef } from 'react';
import type { FC } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

interface MapProps {
    center?: [number, number];
    zoom?: number;
    className?: string;
    markers?: Array<{
        lat: number;
        lng: number;
        title: string;
        description?: string;
    }>;
}

const Map: FC<MapProps> = ({
    center = [0, 20],
    zoom = 2,
    className = "h-[500px] w-full rounded-2xl",
    markers = []
}) => {
    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<maplibregl.Map | null>(null);

    useEffect(() => {
        if (map.current) return;
        if (!mapContainer.current) return;

        map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: {
                version: 8,
                sources: {
                    'satellite-tiles': {
                        type: 'raster',
                        tiles: [
                            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
                        ],
                        tileSize: 256,
                        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
                    }
                },
                layers: [
                    {
                        id: 'simple-tiles',
                        type: 'raster',
                        source: 'satellite-tiles',
                        minzoom: 0,
                        maxzoom: 22
                    }
                ]
            },
            center: center,
            zoom: zoom,
        });

        map.current.addControl(new maplibregl.NavigationControl(), 'top-right');

        markers.forEach(marker => {
            const popupContent = `
                <div class="p-3 min-w-[200px] font-sans">
                    <h3 class="text-sm font-black text-slate-900 mb-1">${marker.title}</h3>
                    <p class="text-xs text-slate-500 mb-3">${marker.description || ''}</p>
                    <a href="/hotels?q=${encodeURIComponent(marker.title)}" 
                       class="block w-full text-center py-2 px-3 bg-primary text-white text-[10px] font-bold rounded-lg shadow-lg hover:bg-primary/90 transition-all no-underline">
                       Explore Stays
                    </a>
                </div>
            `;

            new maplibregl.Marker({ color: "#3B82F6" })
                .setLngLat([marker.lng, marker.lat])
                .setPopup(new maplibregl.Popup({
                    offset: 35,
                    maxWidth: '220px',
                    className: 'custom-map-popup'
                }).setHTML(popupContent))
                .addTo(map.current!);
        });

        return () => {
            map.current?.remove();
            map.current = null;
        };
    }, [center, zoom, markers]);

    return (
        <div className="relative group">
            <div ref={mapContainer} className={`${className} shadow-2xl glass-card overflow-hidden`} />
        </div>
    );
};

export default Map;
