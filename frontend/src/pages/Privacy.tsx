import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';

export default function Privacy() {
    return (
        <div className="min-h-screen pt-24 pb-16 px-6">
            <div className="max-w-4xl mx-auto">
                <div className="flex items-center gap-3 mb-8">
                    <Shield className="w-10 h-10 text-primary" />
                    <h1 className="text-4xl font-black">Privacy Policy</h1>
                </div>

                <p className="text-slate-600 dark:text-slate-400 mb-8">
                    Last updated: January 8, 2026
                </p>

                <div className="prose prose-slate dark:prose-invert max-w-none space-y-8">
                    <section>
                        <h2 className="text-2xl font-bold mb-4">1. Information We Collect</h2>
                        <p>We collect information you provide directly to us when you:</p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li>Create an account</li>
                            <li>Make a booking</li>
                            <li>Contact our support team</li>
                            <li>Subscribe to our newsletter</li>
                        </ul>
                        <p className="mt-4">This information may include your name, email address, phone number, payment information, and travel preferences.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">2. How We Use Your Information</h2>
                        <p>We use the information we collect to:</p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li>Process your bookings and payments</li>
                            <li>Send you booking confirmations and updates</li>
                            <li>Provide customer support</li>
                            <li>Improve our services and user experience</li>
                            <li>Send promotional communications (with your consent)</li>
                            <li>Detect and prevent fraud</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">3. Information Sharing</h2>
                        <p>We do not sell your personal information. We may share your information with:</p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li><strong>Service Providers:</strong> Hotels, airlines, and other travel partners to fulfill your bookings</li>
                            <li><strong>Payment Processors:</strong> To process your payments securely</li>
                            <li><strong>Analytics Partners:</strong> To understand how our service is used (anonymized data)</li>
                            <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">4. Data Security</h2>
                        <p>We implement industry-standard security measures to protect your personal information, including:</p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li>SSL/TLS encryption for data transmission</li>
                            <li>Secure password hashing</li>
                            <li>Regular security audits</li>
                            <li>Access controls and authentication</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">5. Your Rights</h2>
                        <p>You have the right to:</p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li>Access your personal information</li>
                            <li>Correct inaccurate information</li>
                            <li>Request deletion of your data</li>
                            <li>Opt-out of marketing communications</li>
                            <li>Export your data</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">6. Cookies</h2>
                        <p>We use cookies and similar technologies to enhance your experience. See our <Link to="/cookies" className="text-primary hover:underline">Cookie Policy</Link> for more details.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">7. Contact Us</h2>
                        <p>If you have questions about this Privacy Policy, please contact us at:</p>
                        <p className="mt-2">
                            Email: privacy@worldtour.com<br />
                            Address: 123 Travel Street, Adventure City, AC 12345
                        </p>
                    </section>
                </div>

                <div className="mt-12 pt-8 border-t border-slate-200 dark:border-slate-800">
                    <Link to="/" className="text-primary hover:underline font-bold">
                        ← Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
}
