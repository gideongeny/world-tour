import { useCurrency } from '../context/CurrencyContext';
import { Globe } from 'lucide-react';

const CURRENCIES = [
    { code: 'USD', name: 'US Dollar', symbol: '$' },
    { code: 'EUR', name: 'Euro', symbol: '€' },
    { code: 'GBP', name: 'British Pound', symbol: '£' },
    { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
    { code: 'AUD', name: 'Australian Dollar', symbol: 'A$' },
    { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$' },
    { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF' },
    { code: 'CNY', name: 'Chinese Yuan', symbol: '¥' },
    { code: 'INR', name: 'Indian Rupee', symbol: '₹' }
];

export default function CurrencySelector() {
    const { currency, setCurrency } = useCurrency();

    return (
        <div className="relative">
            <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-white/10 dark:bg-slate-800/50 backdrop-blur-sm border border-white/20">
                <Globe className="w-4 h-4" />
                <select
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="bg-transparent outline-none cursor-pointer font-bold text-sm pr-2"
                >
                    {CURRENCIES.map((curr) => (
                        <option key={curr.code} value={curr.code} className="bg-slate-900 text-white">
                            {curr.code} ({curr.symbol})
                        </option>
                    ))}
                </select>
            </div>
        </div>
    );
}
