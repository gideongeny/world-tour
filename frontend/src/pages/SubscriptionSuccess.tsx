import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';

const SubscriptionSuccess: React.FC = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const sessionId = searchParams.get('session_id');

    useEffect(() => {
        // Redirect to home after 5 seconds
        const timer = setTimeout(() => {
            navigate('/');
        }, 5000);

        return () => clearTimeout(timer);
    }, [navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center px-6">
            <div className="text-center max-w-md">
                <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
                <h1 className="text-4xl font-black mb-4">Welcome to World Tour Plus!</h1>
                <p className="text-xl text-slate-600 dark:text-slate-400 mb-8">
                    Your subscription is now active. Enjoy ad-free browsing and exclusive deals!
                </p>
                <button
                    onClick={() => navigate('/')}
                    className="px-8 py-3 bg-primary text-white rounded-xl font-bold hover:bg-primary/90 transition-all"
                >
                    Start Exploring
                </button>
            </div>
        </div>
    );
};

export default SubscriptionSuccess;
