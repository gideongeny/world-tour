import { Link } from 'react-router-dom';
import { Cookie } from 'lucide-react';

export default function Cookies() {
    return (
        <div className="min-h-screen pt-24 pb-16 px-6">
            <div className="max-w-4xl mx-auto">
                <div className="flex items-center gap-3 mb-8">
                    <Cookie className="w-10 h-10 text-primary" />
                    <h1 className="text-4xl font-black">Cookie Policy</h1>
                </div>

                <p className="text-slate-600 dark:text-slate-400 mb-8">
                    Last updated: January 8, 2026
                </p>

                <div className="prose prose-slate dark:prose-invert max-w-none space-y-8">
                    <section>
                        <h2 className="text-2xl font-bold mb-4">What Are Cookies?</h2>
                        <p>Cookies are small text files stored on your device when you visit our website. They help us provide you with a better experience by remembering your preferences and understanding how you use our service.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">Types of Cookies We Use</h2>

                        <div className="space-y-6">
                            <div>
                                <h3 className="text-xl font-bold mb-2">1. Essential Cookies</h3>
                                <p><strong>Purpose:</strong> Required for the website to function properly</p>
                                <p><strong>Examples:</strong></p>
                                <ul className="list-disc pl-6 space-y-1">
                                    <li>User authentication</li>
                                    <li>Security features</li>
                                    <li>Shopping cart functionality</li>
                                </ul>
                                <p className="mt-2"><strong>Duration:</strong> Session or 30 days</p>
                            </div>

                            <div>
                                <h3 className="text-xl font-bold mb-2">2. Preference Cookies</h3>
                                <p><strong>Purpose:</strong> Remember your settings and preferences</p>
                                <p><strong>Examples:</strong></p>
                                <ul className="list-disc pl-6 space-y-1">
                                    <li>Selected currency (USD, EUR, etc.)</li>
                                    <li>Language preference</li>
                                    <li>Dark mode setting</li>
                                </ul>
                                <p className="mt-2"><strong>Duration:</strong> 1 year</p>
                            </div>

                            <div>
                                <h3 className="text-xl font-bold mb-2">3. Analytics Cookies</h3>
                                <p><strong>Purpose:</strong> Help us understand how visitors use our website</p>
                                <p><strong>Examples:</strong></p>
                                <ul className="list-disc pl-6 space-y-1">
                                    <li>Page views and navigation patterns</li>
                                    <li>Time spent on pages</li>
                                    <li>Error messages encountered</li>
                                </ul>
                                <p className="mt-2"><strong>Duration:</strong> 2 years</p>
                            </div>

                            <div>
                                <h3 className="text-xl font-bold mb-2">4. Marketing Cookies</h3>
                                <p><strong>Purpose:</strong> Deliver relevant advertisements</p>
                                <p><strong>Examples:</strong></p>
                                <ul className="list-disc pl-6 space-y-1">
                                    <li>Tracking ad performance</li>
                                    <li>Personalizing ad content</li>
                                    <li>Retargeting campaigns</li>
                                </ul>
                                <p className="mt-2"><strong>Duration:</strong> 90 days</p>
                            </div>
                        </div>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">Third-Party Cookies</h2>
                        <p>We use services from third parties that may set their own cookies:</p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li><strong>Google Analytics:</strong> Website analytics</li>
                            <li><strong>Stripe:</strong> Payment processing</li>
                            <li><strong>Social Media:</strong> Social sharing features</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">Managing Cookies</h2>
                        <p>You can control cookies through your browser settings:</p>

                        <div className="mt-4 space-y-3">
                            <p><strong>Chrome:</strong> Settings → Privacy and Security → Cookies</p>
                            <p><strong>Firefox:</strong> Options → Privacy & Security → Cookies</p>
                            <p><strong>Safari:</strong> Preferences → Privacy → Cookies</p>
                            <p><strong>Edge:</strong> Settings → Privacy → Cookies</p>
                        </div>

                        <p className="mt-4 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                            <strong>Note:</strong> Disabling essential cookies may affect website functionality.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">Updates to This Policy</h2>
                        <p>We may update this Cookie Policy from time to time. We will notify you of any significant changes by posting the new policy on this page.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">Contact Us</h2>
                        <p>If you have questions about our use of cookies:</p>
                        <p className="mt-2">
                            Email: support@worldtour.com<br />
                            Address: Kenyatta Avenue, CBD, Nairobi, Kenya
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
