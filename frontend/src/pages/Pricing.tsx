import React, { useState, useEffect } from 'react';
import { Check, X, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface PricingPlan {
    name: string;
    price: number;
    interval: 'month' | 'year';
    features: string[];
    popular?: boolean;
}

const Pricing: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [isSubscribed, setIsSubscribed] = useState(false);

    useEffect(() => {
        // Check subscription status
        fetch('/api/payments/subscription-status', {
            credentials: 'include'
        })
            .then(res => res.json())
            .then(data => setIsSubscribed(data.subscribed))
            .catch(console.error);
    }, []);

    const plans: PricingPlan[] = [
        {
            name: 'Free',
            price: 0,
            interval: 'month',
            features: [
                'Browse destinations',
                'Search hotels & flights',
                'Basic AI assistant',
                'Standard ads'
            ]
        },
        {
            name: 'World Tour Plus',
            price: 9.99,
            interval: 'month',
            popular: true,
            features: [
                '✨ Ad-free experience',
                '🎯 Exclusive deals & discounts',
                '🤖 Priority AI assistant',
                '📊 Advanced trip planning',
                '🔔 Price drop alerts',
                '💎 Early access to features'
            ]
        },
        {
            name: 'World Tour Plus',
            price: 79.99,
            interval: 'year',
            features: [
                'All monthly features',
                '💰 Save $40/year',
                '🎁 Bonus travel guides',
                '⭐ VIP support'
            ]
        }
    ];

    const handleSubscribe = async (plan: PricingPlan) => {
        if (plan.price === 0) return;

        setLoading(true);

        try {
            const response = await fetch('/api/payments/create-subscription', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    plan: plan.interval === 'month' ? 'monthly' : 'yearly'
                })
            });

            // Check if user is not authenticated
            if (response.status === 401) {
                alert('Please log in to subscribe to World Tour Plus');
                navigate('/login');
                return;
            }

            const data = await response.json();

            if (data.checkout_url) {
                window.location.href = data.checkout_url;
            } else if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                alert('Stripe is not configured yet. Please complete the Stripe setup guide first.');
            }
        } catch (error) {
            console.error('Subscription error:', error);
            alert('Unable to connect to payment system. Stripe may not be configured yet.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="pt-24 pb-20 px-6 max-w-7xl mx-auto">
            <div className="text-center mb-16">
                <h1 className="text-5xl font-black mb-4 tracking-tight">Choose Your Plan</h1>
                <p className="text-xl text-slate-500 max-w-2xl mx-auto">
                    Unlock premium features and exclusive travel deals
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                {plans.map((plan, index) => (
                    <div
                        key={index}
                        className={`relative bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-xl border-2 transition-all hover:scale-105 ${plan.popular
                            ? 'border-primary shadow-2xl shadow-primary/20'
                            : 'border-slate-200 dark:border-slate-700'
                            }`}
                    >
                        {plan.popular && (
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-white px-4 py-1 rounded-full text-sm font-bold flex items-center gap-1">
                                <Sparkles className="w-4 h-4" />
                                Most Popular
                            </div>
                        )}

                        <div className="text-center mb-6">
                            <h3 className="text-2xl font-black mb-2">{plan.name}</h3>
                            <div className="flex items-baseline justify-center gap-1">
                                <span className="text-4xl font-black">${plan.price}</span>
                                <span className="text-slate-500">/{plan.interval}</span>
                            </div>
                        </div>

                        <ul className="space-y-3 mb-8">
                            {plan.features.map((feature, i) => (
                                <li key={i} className="flex items-start gap-2">
                                    <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                                    <span className="text-slate-700 dark:text-slate-300">{feature}</span>
                                </li>
                            ))}
                        </ul>

                        <button
                            onClick={() => handleSubscribe(plan)}
                            disabled={loading || (plan.price === 0) || isSubscribed}
                            className={`w-full py-3 rounded-xl font-bold transition-all ${plan.popular
                                ? 'bg-primary text-white hover:bg-primary/90 shadow-lg shadow-primary/30'
                                : 'bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600'
                                } disabled:opacity-50 disabled:cursor-not-allowed`}
                        >
                            {isSubscribed ? 'Current Plan' : plan.price === 0 ? 'Current Plan' : 'Subscribe Now'}
                        </button>
                    </div>
                ))}
            </div>

            <div className="mt-16 text-center text-slate-500">
                <p>Cancel anytime. No hidden fees. 30-day money-back guarantee.</p>
            </div>
        </div>
    );
};

export default Pricing;
