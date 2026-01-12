import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Mail, Lock } from 'lucide-react';
import { API_BASE_URL } from '../config';
import { useUser } from '../context/UserContext';

export default function Signup() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useUser();

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await res.json();

            if (res.ok && data.success) {
                // Auto login after signup
                login({ username, email });
                navigate('/');
            } else {
                setError(data.error || 'Registration failed');
            }
        } catch (err) {
            console.error('Signup error:', err);
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="pt-32 pb-20 px-6 min-h-screen flex items-center justify-center bg-background">
            <div className="bg-white dark:bg-slate-800 p-10 rounded-3xl shadow-2xl w-full max-w-md border border-slate-100 dark:border-slate-700">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-primary/10 text-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <User className="w-8 h-8" />
                    </div>
                    <h1 className="text-3xl font-black tracking-tight">Create Account</h1>
                    <p className="text-slate-500">Join World Tour today</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 text-sm font-bold text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSignup} className="space-y-4">
                    <div>
                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Username</label>
                        <div className="relative">
                            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                            <input
                                type="text"
                                required
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                className="w-full bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-primary/20 px-5 py-3 pl-12 rounded-xl outline-none font-bold transition-all"
                                placeholder="johndoe"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Email</label>
                        <div className="relative">
                            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                className="w-full bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-primary/20 px-5 py-3 pl-12 rounded-xl outline-none font-bold transition-all"
                                placeholder="john@example.com"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                className="w-full bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-primary/20 px-5 py-3 pl-12 rounded-xl outline-none font-bold transition-all"
                                placeholder="••••••••"
                            />
                        </div>
                    </div>
                    <button
                        disabled={loading}
                        className={`w-full bg-primary text-white py-4 rounded-xl font-black shadow-lg shadow-primary/30 hover:bg-primary/90 transition-all mt-4 ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
                    >
                        {loading ? 'Creating Account...' : 'Sign Up'}
                    </button>
                </form>

                <p className="text-center mt-8 text-slate-500 font-medium">
                    Already have an account? <Link to="/login" className="text-primary font-bold hover:underline">Log In</Link>
                </p>
            </div>
        </div>
    );
}
