import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus } from 'lucide-react';

function Signup() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const res = await fetch('https://world-tour-backend.vercel.app/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await res.json();

            if (res.ok && data.success) {
                // Success
                navigate('/');
            } else {
                setError(data.error || 'Registration failed');
            }
        } catch (err) {
            setError('Something went wrong. Please try again.');
        }
    };

    return (
        <div className="pt-32 pb-20 px-6 min-h-screen flex items-center justify-center">
            <div className="bg-white dark:bg-slate-800 p-10 rounded-3xl shadow-2xl w-full max-w-md border border-slate-100 dark:border-slate-700">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-secondary/10 text-secondary rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <UserPlus className="w-8 h-8" />
                    </div>
                    <h1 className="text-3xl font-black tracking-tight">Create Account</h1>
                    <p className="text-slate-500">Join thousands of travelers today</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 text-sm font-bold text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSignup} className="space-y-6">
                    <div>
                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-secondary/20 px-5 py-3 rounded-xl outline-none font-bold transition-all"
                            placeholder="Choose a username"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-secondary/20 px-5 py-3 rounded-xl outline-none font-bold transition-all"
                            placeholder="Enter your email"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-secondary/20 px-5 py-3 rounded-xl outline-none font-bold transition-all"
                            placeholder="Create a password"
                        />
                    </div>
                    <button className="w-full bg-secondary text-white py-4 rounded-xl font-black shadow-lg shadow-secondary/30 hover:bg-secondary/90 transition-all">
                        Sign Up
                    </button>
                </form>

                <p className="text-center mt-8 text-slate-500 font-medium">
                    Already have an account? <Link to="/login" className="text-secondary font-bold hover:underline">Sign In</Link>
                </p>
            </div>
        </div>
    );
}

export default Signup;
