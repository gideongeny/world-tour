import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { useCurrency } from '../context/CurrencyContext';
import { API_BASE_URL } from '../config';
import { Navigate, Link } from 'react-router-dom';
import { Heart, User, Package, Calendar, MapPin, Trash2, ShieldCheck, CreditCard } from 'lucide-react';
import Price from '../components/Price';

interface SavedItem {
    id: number;
    type: string;
    data: any;
    created_at: string;
}

interface UserProfile {
    username: string;
    email: string;
    subscription: {
        active: boolean;
        plan: string;
        expires_at: string | null;
    };
    stats: {
        saved_trips: number;
    };
}

const Profile = () => {
    const { isAuthenticated, user } = useUser();
    const { currency } = useCurrency();
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [wishlist, setWishlist] = useState<SavedItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isAuthenticated) {
            fetchProfile();
            fetchWishlist();
        }
    }, [isAuthenticated]);

    const fetchProfile = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/user/profile`, {
                credentials: 'include'
            });
            if (res.ok) {
                const data = await res.json();
                setProfile(data);
            }
        } catch (error) {
            console.error('Error fetching profile:', error);
        }
    };

    const fetchWishlist = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/user/wishlist`, {
                credentials: 'include'
            });
            if (res.ok) {
                const data = await res.json();
                setWishlist(data);
            }
        } catch (error) {
            console.error('Error fetching wishlist:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRemove = async (id: number) => {
        if (!confirm('Remove this saved trip?')) return;
        try {
            const res = await fetch(`${API_BASE_URL}/api/user/wishlist/${id}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            if (res.ok) {
                setWishlist(prev => prev.filter(item => item.id !== id));
                // Update stats locally
                if (profile) {
                    setProfile({
                        ...profile,
                        stats: { ...profile.stats, saved_trips: profile.stats.saved_trips - 1 }
                    });
                }
            }
        } catch (error) {
            alert('Failed to remove item');
        }
    };

    if (!isAuthenticated) return <Navigate to="/login" />;
    if (loading) return <div className="min-h-screen pt-24 flex justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;

    return (
        <div className="min-h-screen pt-24 pb-12 px-6">
            <div className="max-w-6xl mx-auto space-y-8">

                {/* Header / Profile Card */}
                <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-xl border border-slate-100 dark:border-slate-700 flex flex-col md:flex-row gap-8 items-start">
                    <div className="p-4 bg-primary/10 rounded-full">
                        <User className="w-16 h-16 text-primary" />
                    </div>
                    <div className="flex-1">
                        <h1 className="text-3xl font-bold mb-2 text-slate-900 dark:text-white">{profile?.username}</h1>
                        <p className="text-slate-500 dark:text-slate-400 mb-4">{profile?.email}</p>

                        <div className="flex flex-wrap gap-4">
                            <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-900 rounded-lg">
                                <MapPin className="w-4 h-4 text-primary" />
                                <span className="font-bold">{profile?.stats.saved_trips}</span>
                                <span className="text-sm text-slate-500">Saved Trips</span>
                            </div>
                            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${profile?.subscription.active ? 'bg-amber-100 border-amber-200 text-amber-800' : 'bg-slate-100 border-slate-200 text-slate-600'}`}>
                                <ShieldCheck className="w-4 h-4" />
                                <span className="font-bold capitalize">{profile?.subscription.active ? profile?.subscription.plan + ' Plan' : 'Free Plan'}</span>
                            </div>
                        </div>
                    </div>

                    {!profile?.subscription.active && (
                        <div className="flex flex-col gap-3 items-end">
                            <p className="text-sm text-slate-500 max-w-[200px] text-right">Upgrade to unlock exclusive deals and AI planning.</p>
                            <Link to="/pricing" className="px-6 py-2 bg-primary text-white rounded-full font-bold hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20">
                                Upgrade Now
                            </Link>
                        </div>
                    )}
                </div>

                {/* Saved Trips Section */}
                <div>
                    <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                        <Heart className="w-6 h-6 text-red-500 fill-current" />
                        My Saved Trips
                    </h2>

                    {wishlist.length === 0 ? (
                        <div className="text-center py-12 bg-white/50 dark:bg-slate-800/50 rounded-2xl border-dashed border-2 border-slate-300 dark:border-slate-700">
                            <Package className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                            <p className="text-lg text-slate-500 font-medium">No saved trips yet.</p>
                            <Link to="/" className="text-primary font-bold hover:underline mt-2 inline-block">Start Exploring</Link>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {wishlist.map((item) => (
                                <div key={item.id} className="group bg-white dark:bg-slate-800 rounded-xl overflow-hidden shadow-lg border border-slate-100 dark:border-slate-700 hover:shadow-2xl transition-all duration-300">
                                    <div className="relative h-48 overflow-hidden">
                                        <img
                                            src={item.data.image_url || 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&q=80'}
                                            alt={item.data.name || 'Saved Item'}
                                            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                        />
                                        <div className="absolute top-4 right-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur px-3 py-1 rounded-full text-xs font-bold shadow-sm">
                                            {item.type.toUpperCase()}
                                        </div>
                                    </div>
                                    <div className="p-5">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="text-lg font-bold text-slate-900 dark:text-white line-clamp-1">{item.data.name || 'Unknown Item'}</h3>
                                            {item.data.rating && (
                                                <div className="flex items-center text-amber-500 text-sm font-bold bg-amber-50 dark:bg-amber-900/20 px-1.5 py-0.5 rounded">
                                                    ★ {item.data.rating}
                                                </div>
                                            )}
                                        </div>
                                        {item.data.country && <p className="text-sm text-slate-500 mb-4 flex items-center gap-1"><MapPin className="w-3 h-3" /> {item.data.country}</p>}

                                        <div className="flex items-center justify-between mt-4">
                                            <div className="text-primary font-bold text-lg">
                                                {item.data.price ? <Price amount={item.data.price} /> : 'Check Price'}
                                            </div>
                                            <button
                                                onClick={() => handleRemove(item.id)}
                                                className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-colors"
                                                title="Remove from saved"
                                            >
                                                <Trash2 className="w-5 h-5" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Profile;
