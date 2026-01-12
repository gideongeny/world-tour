import { createContext, useContext, useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import type { ReactNode } from 'react';

interface CurrencyContextType {
    currency: string;
    rates: Record<string, number>;
    setCurrency: (currency: string) => void;
    convert: (amount: number) => number;
    formatPrice: (amount: number) => string;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

const CURRENCY_SYMBOLS: Record<string, string> = {
    USD: '$',
    EUR: '€',
    GBP: '£',
    JPY: '¥',
    AUD: 'A$',
    CAD: 'C$',
    CHF: 'CHF',
    CNY: '¥',
    INR: '₹',
    KES: 'KSh',
    ZAR: 'R'
};

export const CurrencyProvider = ({ children }: { children: ReactNode }) => {
    const [currency, setCurrencyState] = useState<string>('USD');
    const [rates, setRates] = useState<Record<string, number>>({ USD: 1.0 });

    useEffect(() => {
        // Load saved currency from localStorage
        const savedCurrency = localStorage.getItem('currency');
        if (savedCurrency) {
            setCurrencyState(savedCurrency);
        }

        // Fetch exchange rates
        fetchRates();

        // Refresh rates every 24 hours
        const interval = setInterval(fetchRates, 24 * 60 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    const fetchRates = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/currency/rates`);
            const data = await res.json();
            if (data.success && data.rates) {
                setRates(data.rates);
            }
        } catch (error) {
            console.error('Failed to fetch exchange rates:', error);
            // Use fallback rates
            setRates({
                USD: 1.0,
                EUR: 0.85,
                GBP: 0.73,
                JPY: 110.5,
                AUD: 1.35,
                CAD: 1.25,
                CHF: 0.92,
                CNY: 6.45,
                INR: 74.5,
                KES: 130.0,
                ZAR: 18.5
            });
        }
    };

    const setCurrency = (newCurrency: string) => {
        setCurrencyState(newCurrency);
        localStorage.setItem('currency', newCurrency);
    };

    const convert = (amount: number): number => {
        const rate = rates[currency] || 1.0;
        return amount * rate;
    };

    const formatPrice = (amount: number): string => {
        const converted = convert(amount);
        const symbol = CURRENCY_SYMBOLS[currency] || currency;

        // Format based on currency
        if (currency === 'JPY') {
            return `${symbol}${Math.round(converted).toLocaleString()}`;
        }
        return `${symbol}${converted.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
    };

    return (
        <CurrencyContext.Provider value={{ currency, rates, setCurrency, convert, formatPrice }}>
            {children}
        </CurrencyContext.Provider>
    );
};

export const useCurrency = () => {
    const context = useContext(CurrencyContext);
    if (!context) {
        throw new Error('useCurrency must be used within CurrencyProvider');
    }
    return context;
};
