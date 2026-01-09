import React, { useState } from 'react';
import { Shield, Check, X } from 'lucide-react';

interface InsuranceWidgetProps {
    destination: string;
    tripCost?: number;
    travelers?: number;
    onSelect?: (selected: boolean) => void;
}

const InsuranceWidget: React.FC<InsuranceWidgetProps> = ({
    destination,
    tripCost = 1000,
    travelers = 1,
    onSelect
}) => {
    const [selected, setSelected] = useState(false);

    // Estimate insurance cost (typically 4-10% of trip cost)
    const estimatedCost = Math.round(tripCost * 0.06);

    const handleToggle = () => {
        const newValue = !selected;
        setSelected(newValue);
        onSelect?.(newValue);
    };

    const handleGetQuote = () => {
        // World Nomads affiliate link
        const affiliateId = 'YOUR_WORLD_NOMADS_AFFILIATE_ID';
        const url = `https://www.worldnomads.com/travel-insurance?affiliate=${affiliateId}&destination=${encodeURIComponent(destination)}&travelers=${travelers}&trip_cost=${tripCost}`;

        // Track affiliate click
        fetch('/api/affiliate/track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                affiliateType: 'insurance',
                destination: destination
            })
        });

        window.open(url, '_blank');
    };

    return (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl p-6 border-2 border-blue-200 dark:border-blue-800">
            <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-500 rounded-xl">
                    <Shield className="w-6 h-6 text-white" />
                </div>

                <div className="flex-1">
                    <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                        Travel Insurance
                        <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">Recommended</span>
                    </h3>

                    <p className="text-slate-600 dark:text-slate-300 mb-4">
                        Protect your trip from unexpected cancellations, medical emergencies, and lost baggage.
                    </p>

                    <div className="grid grid-cols-2 gap-3 mb-4">
                        <div className="flex items-center gap-2 text-sm">
                            <Check className="w-4 h-4 text-green-500" />
                            <span>Trip cancellation</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Check className="w-4 h-4 text-green-500" />
                            <span>Medical coverage</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Check className="w-4 h-4 text-green-500" />
                            <span>Lost baggage</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Check className="w-4 h-4 text-green-500" />
                            <span>24/7 assistance</span>
                        </div>
                    </div>

                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-slate-500">Estimated from</p>
                            <p className="text-2xl font-black text-blue-600">${estimatedCost}</p>
                        </div>

                        <button
                            onClick={handleGetQuote}
                            className="px-6 py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/30"
                        >
                            Get Free Quote
                        </button>
                    </div>
                </div>
            </div>

            <div className="mt-4 pt-4 border-t border-blue-200 dark:border-blue-800">
                <p className="text-xs text-slate-500">
                    Powered by World Nomads • Trusted by millions of travelers worldwide
                </p>
            </div>
        </div>
    );
};

export default InsuranceWidget;
