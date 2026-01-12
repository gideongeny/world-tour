
import { useState, ImgHTMLAttributes } from 'react';
import { ImageOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ImageWithFallbackProps extends ImgHTMLAttributes<HTMLImageElement> {
    fallbackSrc?: string;
    fallbackComponent?: React.ReactNode;
}

const ImageWithFallback = ({
    src,
    alt,
    className,
    fallbackSrc = 'https://images.unsplash.com/photo-1488085061387-422e29b40080?auto=format&fit=crop&q=80', // Default generic travel fallback
    fallbackComponent,
    ...props
}: ImageWithFallbackProps) => {
    const [error, setError] = useState(false);
    const [loading, setLoading] = useState(true);

    const handleLoad = () => {
        setLoading(false);
    };

    const handleError = () => {
        if (!error) {
            setError(true);
            setLoading(false);
        }
    };

    if (error && fallbackComponent) {
        return <>{fallbackComponent}</>;
    }

    if (error) {
        // Use a persistent fallback that is guaranteed to work (or a local asset if available)
        // If the fallbackSrc also fails, we show an icon
        return (
            <div className={cn("relative overflow-hidden bg-slate-100 dark:bg-slate-800 flex items-center justify-center", className)}>
                {/* Try to render fallback image, if it fails, show icon */}
                <img
                    src={fallbackSrc}
                    alt={alt || "Fallback"}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                        // If fallback fails, hide image and show icon
                        e.currentTarget.style.display = 'none';
                        e.currentTarget.parentElement?.classList.add('fallback-failed');
                    }}
                />
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none hidden [.fallback-failed_&]:flex">
                    <ImageOff className="w-8 h-8 text-slate-400" />
                </div>
            </div>
        );
    }

    return (
        <div className={cn("relative overflow-hidden", className)}>
            {loading && (
                <div className="absolute inset-0 bg-slate-200 dark:bg-slate-700 animate-pulse" />
            )}
            <img
                src={src}
                alt={alt}
                onLoad={handleLoad}
                onError={handleError}
                className={cn("w-full h-full object-cover transition-opacity duration-300", loading ? 'opacity-0' : 'opacity-100')}
                {...props}
            />
        </div>
    );
};

export default ImageWithFallback;
