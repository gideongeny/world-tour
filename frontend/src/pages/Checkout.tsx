import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CreditCard, ShieldCheck, Mail, User, Phone, CheckCircle2 } from 'lucide-react';
import ImageWithFallback from '../components/ui/image-with-fallback';
import { API_BASE_URL } from '../config';

function Checkout() {
    const location = useLocation();
    const navigate = useNavigate();

    // Check for Stripe return states
    const query = new URLSearchParams(location.search);
    const success = query.get('success') === 'true';

    const [step, setStep] = useState(success ? 3 : 1);
    const [loading, setLoading] = useState(false);

    const itemType = query.get('type') || 'Booking';
    const itemName = query.get('name') || 'Travel Selection';
    const itemPrice = query.get('price') || '0';
    const itemImage = query.get('image') || 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&q=80';

    const handleConfirmBooking = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/booking/create-checkout-session`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: itemName,
                    price: itemPrice,
                    type: itemType
                })
            });
            const data = await response.json();
            if (data.url) {
                // Redirect to Stripe Checkout
                window.location.href = data.url;
            } else {
                throw new Error(data.error || 'Failed to create session');
            }
        } catch (err) {
            console.error("Payment failed:", err);
            alert("Payment failed to initialize. Please try again.");
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="pt-32 pb-20 px-6 max-w-2xl mx-auto text-center">
                <div className="mb-8 flex justify-center">
                    <div className="w-24 h-24 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center animate-bounce">
                        <CheckCircle2 className="w-12 h-12 text-green-500" />
                    </div>
                </div>
                <h1 className="text-4xl font-black mb-4">Booking Confirmed!</h1>
                <p className="text-xl text-slate-500 mb-8">
                    Your {itemType.toLowerCase()} to <strong>{itemName}</strong> has been successfully booked.
                    A confirmation email has been sent to your inbox.
                </p>
                <div className="bg-slate-50 dark:bg-slate-800 p-6 rounded-2xl mb-8 border border-dashed border-slate-200 dark:border-slate-700">
                    <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-2">Booking ID</p>
                    <p className="text-2xl font-mono font-bold">WT-{Math.random().toString(36).substr(2, 9).toUpperCase()}</p>
                </div>
                <button
                    onClick={() => navigate('/')}
                    className="px-8 py-4 bg-primary text-white rounded-2xl font-bold shadow-xl shadow-primary/30 hover:bg-primary/90 transition-all"
                >
                    Return to Home
                </button>
            </div>
        );
    }

    return (
        <div className="pt-32 pb-20 px-6 max-w-6xl mx-auto min-h-screen">
            <div className="flex flex-col lg:flex-row gap-12">
                {/* Left Side: Forms */}
                <div className="flex-1">
                    <div className="flex items-center gap-4 mb-8">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${step >= 1 ? 'bg-primary text-white' : 'bg-slate-200 text-slate-500'}`}>1</div>
                        <div className="h-0.5 w-12 bg-slate-200"></div>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${step >= 2 ? 'bg-primary text-white' : 'bg-slate-200 text-slate-500'}`}>2</div>
                        <h2 className="text-2xl font-black ml-4">{step === 1 ? 'Traveler Details' : 'Payment Method'}</h2>
                    </div>

                    <form onSubmit={(e) => { e.preventDefault(); setStep(2); }} className={step === 1 ? 'block' : 'hidden'}>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                            <div>
                                <label className="block text-xs font-bold text-slate-400 uppercase mb-2">First Name</label>
                                <div className="relative">
                                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                                    <input required type="text" className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl py-3 pl-12 pr-4 outline-none focus:border-primary transition-colors" placeholder="John" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Last Name</label>
                                <input required type="text" className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl py-3 px-4 outline-none focus:border-primary transition-colors" placeholder="Doe" />
                            </div>
                            <div className="md:col-span-2">
                                <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Email Address</label>
                                <div className="relative">
                                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                                    <input required type="email" className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl py-3 pl-12 pr-4 outline-none focus:border-primary transition-colors" placeholder="john@example.com" />
                                </div>
                            </div>
                            <div className="md:col-span-2">
                                <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Phone Number</label>
                                <div className="relative">
                                    <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                                    <input required type="tel" className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl py-3 pl-12 pr-4 outline-none focus:border-primary transition-colors" placeholder="+1 (555) 000-0000" />
                                </div>
                            </div>
                        </div>
                        <button className="w-full py-4 bg-slate-900 dark:bg-white dark:text-slate-900 text-white rounded-2xl font-bold shadow-lg hover:opacity-90 transition-all">
                            Continue to Payment
                        </button>
                    </form>

                    <form onSubmit={handleConfirmBooking} className={step === 2 ? 'block' : 'hidden'}>
                        <div className="bg-slate-50 dark:bg-slate-800 p-6 rounded-2xl mb-8 border border-slate-200 dark:border-slate-700">
                            <div className="flex items-center gap-4 mb-6">
                                <div className="p-3 bg-primary/10 rounded-xl text-primary">
                                    <CreditCard className="w-6 h-6" />
                                </div>
                                <div>
                                    <h3 className="font-bold">Secure Payment</h3>
                                    <p className="text-xs text-slate-500">Industry standard SSL encrypted payment</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Card Number</label>
                                    <input required type="text" className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl py-3 px-4 outline-none focus:border-primary font-mono" placeholder="4242 4242 4242 4242" />
                                </div>
                                <div className="flex gap-4">
                                    <div className="flex-1">
                                        <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Expiry Date</label>
                                        <input required type="text" className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl py-3 px-4 outline-none focus:border-primary font-mono" placeholder="MM / YY" />
                                    </div>
                                    <div className="w-32">
                                        <label className="block text-xs font-bold text-slate-400 uppercase mb-2">CVC</label>
                                        <input required type="text" className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl py-3 px-4 outline-none focus:border-primary font-mono" placeholder="123" />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="flex flex-col gap-4">
                            <button
                                disabled={loading}
                                className="w-full py-4 bg-primary text-white rounded-2xl font-bold shadow-xl shadow-primary/30 hover:bg-primary/90 transition-all flex items-center justify-center gap-2"
                            >
                                {loading ? 'Processing...' : `Pay $${itemPrice} & Confirm Booking`}
                            </button>
                            <button onClick={() => setStep(1)} type="button" className="text-slate-500 font-bold text-sm hover:text-slate-700 dark:hover:text-slate-300">
                                Back to Traveler Details
                            </button>
                        </div>
                    </form>
                </div>

                {/* Right Side: Summary Card */}
                <div className="w-full lg:w-96">
                    <div className="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl overflow-hidden sticky top-32 border border-slate-100 dark:border-slate-700">
                        <div className="h-40 overflow-hidden relative">
                            <ImageWithFallback src={itemImage!} alt={itemName} className="w-full h-full object-cover" />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                            <div className="absolute bottom-4 left-6">
                                <span className="text-primary-foreground bg-primary/20 backdrop-blur-md px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest leading-none mb-1 inline-block">
                                    {itemType}
                                </span>
                                <h3 className="text-white font-bold text-xl">{itemName}</h3>
                            </div>
                        </div>
                        <div className="p-8">
                            <div className="space-y-4 mb-6">
                                <div className="flex justify-between text-slate-500">
                                    <span>Subtotal</span>
                                    <span className="font-bold text-slate-900 dark:text-white">${itemPrice}</span>
                                </div>
                                <div className="flex justify-between text-slate-500">
                                    <span>Service Fee</span>
                                    <span className="font-bold text-slate-900 dark:text-white">$25.00</span>
                                </div>
                                <div className="flex justify-between text-slate-500">
                                    <span>Taxes</span>
                                    <span className="font-bold text-slate-900 dark:text-white">$12.50</span>
                                </div>
                            </div>
                            <div className="pt-6 border-t border-slate-100 dark:border-slate-700 flex justify-between items-end">
                                <div>
                                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Total Amount</p>
                                    <p className="text-3xl font-black text-primary">${(parseFloat(itemPrice) + 37.5).toFixed(2)}</p>
                                </div>
                                <ShieldCheck className="w-8 h-8 text-green-500 mb-1" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Checkout;
