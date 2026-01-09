import { FC, useEffect } from 'react';

const MonetagManager: FC = () => {
    useEffect(() => {
        // Function to inject scripts safely
        const injectScript = (source: string, dataset?: Record<string, string>, async = true) => {
            const script = document.createElement('script');
            script.src = source;
            script.async = async;
            if (dataset) {
                Object.entries(dataset).forEach(([key, value]) => {
                    script.dataset[key] = value;
                });
            }
            document.body.appendChild(script);
        };

        // Function for the specialized self-appending pattern provided by user
        const injectSelfAppendingScript = (zone: string, src: string) => {
            const s = document.createElement('script');
            s.dataset.zone = zone;
            s.src = src;
            const target = [document.documentElement, document.body].filter(Boolean).pop();
            if (target) {
                target.appendChild(s);
            }
        };

        // Delay global script injection to prevent initial page load lag and navigation locking
        const timer = setTimeout(() => {
            // 1. Zone 10436620
            injectSelfAppendingScript('10436620', 'https://al5sm.com/tag.min.js');

            // 2. Zone 10436621
            injectScript('https://3nbf4.com/act/files/tag.min.js?z=10436621', undefined, true);

            // 3. Zone 200188
            injectScript('https://quge5.com/88/tag.min.js', { zone: '200188', cfasync: 'false' });

            // 4. Zone 10436626
            injectSelfAppendingScript('10436626', 'https://nap5k.com/tag.min.js');

            // 5. Zone 10436627
            injectSelfAppendingScript('10436627', 'https://nap5k.com/tag.min.js');

            // 6. Zone 10436628 (Vignette) - Only inject if not already present to avoid multiple overlays
            if (!document.querySelector('script[data-zone="10436628"]')) {
                injectSelfAppendingScript('10436628', 'https://gizokraijaw.net/vignette.min.js');
            }
        }, 3000); // 3-second delay

        return () => clearTimeout(timer);
    }, []);

    return null; // This component handles side effects only
};

export default MonetagManager;
