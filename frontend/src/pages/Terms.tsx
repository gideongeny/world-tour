import { Link } from 'react-router-dom';
import { FileText } from 'lucide-react';

export default function Terms() {
    return (
        <div className="min-h-screen pt-24 pb-16 px-6">
            <div className="max-w-4xl mx-auto">
                <div className="flex items-center gap-3 mb-8">
                    <FileText className="w-10 h-10 text-primary" />
                    <h1 className="text-4xl font-black">Terms of Service</h1>
                </div>

                <p className="text-slate-600 dark:text-slate-400 mb-8">
                    Last updated: January 8, 2026
                </p>

                <div className="prose prose-slate dark:prose-invert max-w-none space-y-8">
                    <section>
                        <h2 className="text-2xl font-bold mb-4">1. Acceptance of Terms</h2>
                        <p>By accessing and using World Tour, you accept and agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our service.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">2. Service Description</h2>
                        <p>World Tour is a travel booking platform that connects users with hotels, flights, and destinations worldwide. We act as an intermediary between you and travel service providers.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">3. User Accounts</h2>
                        <p>To use certain features, you must create an account. You agree to:</p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li>Provide accurate and complete information</li>
                            <li>Maintain the security of your password</li>
                            <li>Notify us immediately of any unauthorized access</li>
                            <li>Be responsible for all activities under your account</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">4. Bookings and Payments</h2>
                        <p><strong>Booking Confirmation:</strong> All bookings are subject to availability and confirmation by the service provider.</p>
                        <p className="mt-4"><strong>Pricing:</strong> Prices are displayed in your selected currency and may vary based on exchange rates.</p>
                        <p className="mt-4"><strong>Payment:</strong> Payment is processed securely through our payment partners. We do not store your full credit card information.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">5. Cancellations and Refunds</h2>
                        <p>Cancellation policies vary by service provider. Please review the specific cancellation terms before booking. Refunds, if applicable, will be processed according to the provider's policy.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">6. User Conduct</h2>
                        <p>You agree not to:</p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li>Use the service for any illegal purpose</li>
                            <li>Attempt to gain unauthorized access to our systems</li>
                            <li>Interfere with the proper functioning of the service</li>
                            <li>Impersonate another person or entity</li>
                            <li>Submit false or misleading information</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">7. Intellectual Property</h2>
                        <p>All content on World Tour, including text, graphics, logos, and software, is the property of World Tour or its licensors and is protected by copyright and trademark laws.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">8. Limitation of Liability</h2>
                        <p>World Tour is not liable for:</p>
                        <ul className="list-disc pl-6 space-y-2">
                            <li>Actions or omissions of third-party service providers</li>
                            <li>Travel delays, cancellations, or changes</li>
                            <li>Loss of personal belongings during travel</li>
                            <li>Indirect, incidental, or consequential damages</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">9. Dispute Resolution</h2>
                        <p>Any disputes arising from these terms will be resolved through binding arbitration in accordance with the laws of [Your Jurisdiction].</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">10. Changes to Terms</h2>
                        <p>We reserve the right to modify these terms at any time. Continued use of the service after changes constitutes acceptance of the new terms.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold mb-4">11. Contact Information</h2>
                        <p>For questions about these Terms of Service:</p>
                        <p className="mt-2">
                            Email: legal@worldtour.com<br />
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
