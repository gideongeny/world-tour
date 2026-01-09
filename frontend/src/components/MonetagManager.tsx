import React, { useEffect } from 'react';

const MonetagManager: React.FC = () => {
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

        // Check frequency capping to reduce annoyance
        const LAST_SHOWN_KEY = 'monetag_last_impression';
        const COOLDOWN_MS = 24 * 60 * 60 * 1000; // 24 hour cooldown - STRICT

        const lastShown = localStorage.getItem(LAST_SHOWN_KEY);
        const now = Date.now();

        if (lastShown && (now - parseInt(lastShown)) < COOLDOWN_MS) {
            console.log('Ad injection skipped due to frequency capping (Strict Mode)');
            return;
        }

        // Delay global script injection to prevent initial page load lag and navigation locking
        const timer = setTimeout(() => {
            // Update timestamp immediately
            localStorage.setItem(LAST_SHOWN_KEY, now.toString());

            // Randomly select ONLY ONE ad format to show per session to avoid spam
            // This is the "Pro" way to monetize without annoying users
            const adStrategies = [
                () => injectSelfAppendingScript('10436620', 'https://al5sm.com/tag.min.js'),
                () => injectScript('https://3nbf4.com/act/files/tag.min.js?z=10436621', undefined, true),
                () => injectScript('https://quge5.com/88/tag.min.js', { zone: '200188', cfasync: 'false' }),
                () => injectSelfAppendingScript('10436626', 'https://nap5k.com/tag.min.js'),
                () => injectSelfAppendingScript('10436628', 'https://gizokraijaw.net/vignette.min.js')
            ];

            const randomStrategy = adStrategies[Math.floor(Math.random() * adStrategies.length)];
            randomStrategy();

        }, 5000); // Increased to 5-second delay for better UX

        return () => clearTimeout(timer);
    }, []);

    return null; // This component handles side effects only
};

export default MonetagManager;
