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
            style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
            center: center,
            zoom: zoom,
        });

        map.current.addControl(new maplibregl.NavigationControl(), 'top-right');

        markers.forEach(marker => {
            new maplibregl.Marker({ color: "#667eea" })
                .setLngLat([marker.lng, marker.lat])
                .setPopup(new maplibregl.Popup({ offset: 25 }).setHTML(
                    `<h3>${marker.title}</h3><p>${marker.description || ''}</p>`
                ))
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
