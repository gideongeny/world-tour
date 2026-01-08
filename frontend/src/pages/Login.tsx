import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogIn } from 'lucide-react';
import { useUser } from '../context/UserContext';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useUser();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const res = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (res.ok && data.success) {
                login({ username, email: data.user?.email || '' });
                navigate('/');
            } else {
                setError(data.error || 'Invalid credentials');
            }
        } catch (err) {
            console.error('Login error:', err);
            setError('Network error. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="pt-32 pb-20 px-6 min-h-screen flex items-center justify-center">
            <div className="bg-white dark:bg-slate-800 p-10 rounded-3xl shadow-2xl w-full max-w-md border border-slate-100 dark:border-slate-700">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-primary/10 text-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <User className="w-8 h-8" />
                    </div>
                    <h1 className="text-3xl font-black tracking-tight">Welcome Back</h1>
                    <p className="text-slate-500">Sign in to continue your journey</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 text-sm font-bold text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-primary/20 px-5 py-3 rounded-xl outline-none font-bold transition-all"
                            placeholder="Enter your username"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-primary/20 px-5 py-3 rounded-xl outline-none font-bold transition-all"
                            placeholder="Enter your password"
                        />
                    </div>
                    <button className="w-full bg-primary text-white py-4 rounded-xl font-black shadow-lg shadow-primary/30 hover:bg-primary/90 transition-all">
                        Sign In
                    </button>
                </form>

                <p className="text-center mt-8 text-slate-500 font-medium">
                    Don't have an account? <Link to="/signup" className="text-primary font-bold hover:underline">Sign Up</Link>
                </p>
            </div>
        </div>
    );
}
