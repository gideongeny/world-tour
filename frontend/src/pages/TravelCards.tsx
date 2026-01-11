import React from 'react';
import { CreditCard, Star, DollarSign, Plane, Gift, Activity } from 'lucide-react';

interface CreditCardOffer {
    name: string;
    issuer: string;
    image: string;
    rating: number;
    annualFee: number;
    signupBonus: string;
    earnRate: string;
    benefits: string[];
    affiliateUrl: string;
    commission: number;
}

const TravelCards: React.FC = () => {
    const cards: CreditCardOffer[] = [
        {
            name: 'Chase Sapphire Preferred',
            issuer: 'Chase',
            image: 'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?w=400&q=80',
            rating: 4.8,
            annualFee: 95,
            signupBonus: '60,000 points ($750 value)',
            earnRate: '2X on travel & dining',
            benefits: [
                'No foreign transaction fees',
                'Trip cancellation insurance',
                'Primary rental car coverage',
                'Transfer points to airlines'
            ],
            affiliateUrl: 'https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred',
            commission: 150
        },
        {
            name: 'Capital One Venture',
            issuer: 'Capital One',
            image: 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400&q=80',
            rating: 4.7,
            annualFee: 95,
            signupBonus: '75,000 miles ($750 value)',
            earnRate: '2X on all purchases',
            benefits: [
                'No foreign transaction fees',
                'Transfer to 15+ airlines',
                'Global Entry credit',
                'Flexible redemption'
            ],
            affiliateUrl: 'https://www.capitalone.com/credit-cards/venture/',
            commission: 100
        },
        {
            name: 'American Express Gold',
            issuer: 'American Express',
            image: 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&q=80',
            rating: 4.9,
            annualFee: 250,
            signupBonus: '60,000 points ($600 value)',
            earnRate: '4X on restaurants & groceries',
            benefits: [
                '$120 dining credit',
                '$120 Uber credit',
                'No preset spending limit',
                'Travel insurance'
            ],
            affiliateUrl: 'https://www.americanexpress.com/us/credit-cards/card/gold-card/',
            commission: 200
        }
    ];

    const handleApply = (card: CreditCardOffer) => {
        // Track affiliate click
        fetch('/api/affiliate/track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                affiliateType: 'credit_card',
                destination: card.name
            })
        });

        window.open(card.affiliateUrl, '_blank');
    };

    return (
        <div className="pt-24 pb-20 px-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="text-center mb-16">
                <h1 className="text-5xl font-black mb-4 tracking-tight">Best Travel Credit Cards 2026</h1>
                <p className="text-xl text-slate-500 max-w-2xl mx-auto">
                    Maximize your travel rewards with these top-rated credit cards. Earn points, miles, and exclusive perks.
                </p>
            </div>

            {/* Why Get a Travel Card */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-16">
                <div className="text-center p-6 bg-white dark:bg-slate-800 rounded-2xl shadow-lg">
                    <Gift className="w-12 h-12 text-primary mx-auto mb-3" />
                    <h3 className="font-bold mb-2">Sign-Up Bonuses</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">Up to $750 in rewards</p>
                </div>
                <div className="text-center p-6 bg-white dark:bg-slate-800 rounded-2xl shadow-lg">
                    <Plane className="w-12 h-12 text-primary mx-auto mb-3" />
                    <h3 className="font-bold mb-2">Travel Benefits</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">Insurance & lounge access</p>
                </div>
                <div className="text-center p-6 bg-white dark:bg-slate-800 rounded-2xl shadow-lg">
                    <DollarSign className="w-12 h-12 text-primary mx-auto mb-3" />
                    <h3 className="font-bold mb-2">No Foreign Fees</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">Save 3% on international</p>
                </div>
                <div className="text-center p-6 bg-white dark:bg-slate-800 rounded-2xl shadow-lg">
                    <Activity className="w-12 h-12 text-primary mx-auto mb-3" />
                    <h3 className="font-bold mb-2">Earn Rewards</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">2-4X on travel & dining</p>
                </div>
            </div>

            {/* Card Comparison */}
            <div className="space-y-8">
                {cards.map((card, index) => (
                    <div
                        key={index}
                        className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl overflow-hidden border-2 border-slate-200 dark:border-slate-700 hover:border-primary transition-all"
                    >
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-8">
                            {/* Card Image & Info */}
                            <div className="text-center md:text-left">
                                <img
                                    src={card.image}
                                    alt={card.name}
                                    className="w-full h-48 object-cover rounded-xl mb-4"
                                />
                                <h3 className="text-2xl font-black mb-2">{card.name}</h3>
                                <p className="text-slate-500 mb-3">{card.issuer}</p>
                                <div className="flex items-center gap-2 justify-center md:justify-start">
                                    <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                                    <span className="font-bold">{card.rating}</span>
                                    <span className="text-slate-500 text-sm">/5.0</span>
                                </div>
                            </div>

                            {/* Benefits */}
                            <div>
                                <div className="mb-4">
                                    <p className="text-sm text-slate-500 mb-1">Sign-up Bonus</p>
                                    <p className="text-lg font-bold text-green-600">{card.signupBonus}</p>
                                </div>
                                <div className="mb-4">
                                    <p className="text-sm text-slate-500 mb-1">Earn Rate</p>
                                    <p className="font-bold">{card.earnRate}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-slate-500 mb-2">Key Benefits</p>
                                    <ul className="space-y-1">
                                        {card.benefits.slice(0, 3).map((benefit, i) => (
                                            <li key={i} className="text-sm flex items-start gap-2">
                                                <span className="text-green-500">✓</span>
                                                <span>{benefit}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {/* CTA */}
                            <div className="flex flex-col justify-between">
                                <div>
                                    <p className="text-sm text-slate-500 mb-1">Annual Fee</p>
                                    <p className="text-3xl font-black mb-6">${card.annualFee}</p>
                                </div>
                                <button
                                    onClick={() => handleApply(card)}
                                    className="w-full py-4 bg-primary text-white rounded-xl font-bold text-lg shadow-xl shadow-primary/30 hover:bg-primary/90 transition-all"
                                >
                                    Apply Now
                                </button>
                                <p className="text-xs text-slate-500 mt-3 text-center">
                                    Recommended for excellent credit
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Disclaimer */}
            <div className="mt-16 p-6 bg-slate-100 dark:bg-slate-800 rounded-2xl">
                <p className="text-sm text-slate-600 dark:text-slate-400">
                    <strong>Disclaimer:</strong> Credit card offers are subject to credit approval. Annual fees, interest rates, and rewards are subject to change. Please review terms and conditions before applying. We may receive compensation when you click on links to credit card offers.
                </p>
            </div>
        </div>
    );
};

export default TravelCards;
