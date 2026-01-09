import { FC, useEffect } from 'react';

const Monetag: FC = () => {
    useEffect(() => {
        // This is a placeholder for the Monetag script the user mentioned.
        // Once the user provides the code, it should be placed here or in index.html.
        const scriptId = "monetag-script";
        if (!document.getElementById(scriptId)) {
            const script = document.createElement("script");
            script.id = scriptId;
            // The user should replace the source with their actual Monetag script URL
            // script.src = "https://example.com/monetag.js"; 
            script.async = true;
            document.head.appendChild(script);
        }
    }, []);

    return (
        <div className="flex justify-center my-8">
            <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-xl border border-dashed border-slate-300 dark:border-slate-600">
                <p className="text-xs text-slate-400 uppercase tracking-widest font-bold">Advertisement by Monetag</p>
                {/* 
                  The user can place their Monetag zone div here.
                  Example: <div id="monetag-zone-12345"></div> 
                */}
                <div className="w-[728px] h-[90px] overflow-hidden rounded-lg">
                    <img
                        src="/premium-ad.png"
                        alt="Premium Travel Deals"
                        className="w-full h-full object-cover transform hover:scale-105 transition-transform duration-700 cursor-pointer"
                    />
                </div>
            </div>
        </div>
    );
};

export default Monetag;
