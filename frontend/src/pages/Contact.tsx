import { useState } from 'react';
import { Mail, Phone, MapPin, Send } from 'lucide-react';

export default function Contact() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        subject: '',
        message: ''
    });
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // In a real app, send to backend
        console.log('Contact form submitted:', formData);
        setSubmitted(true);
        setTimeout(() => setSubmitted(false), 3000);
    };

    return (
        <div className="min-h-screen pt-24 pb-16 px-6">
            <div className="max-w-6xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-5xl font-black mb-4">Get in Touch</h1>
                    <p className="text-xl text-slate-600 dark:text-slate-400">
                        Have questions? We'd love to hear from you.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-12">
                    {/* Contact Info */}
                    <div className="space-y-8">
                        <div>
                            <h2 className="text-2xl font-bold mb-6">Contact Information</h2>

                            <div className="space-y-6">
                                <div className="flex items-start gap-4">
                                    <Mail className="w-6 h-6 text-primary mt-1" />
                                    <div>
                                        <h3 className="font-bold mb-1">Email</h3>
                                        <p className="text-slate-600 dark:text-slate-400">support@worldtour.com</p>
                                        <p className="text-slate-600 dark:text-slate-400">sales@worldtour.com</p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-4">
                                    <Phone className="w-6 h-6 text-primary mt-1" />
                                    <div>
                                        <h3 className="font-bold mb-1">Phone</h3>
                                        <p className="text-slate-600 dark:text-slate-400">+254 720 317 626</p>
                                        <p className="text-sm text-slate-500">Mon-Fri, 9am-6pm EAT</p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-4">
                                    <MapPin className="w-6 h-6 text-primary mt-1" />
                                    <div>
                                        <h3 className="font-bold mb-1">Office</h3>
                                        <p className="text-slate-600 dark:text-slate-400">
                                            Kenyatta Avenue, CBD<br />
                                            Nairobi, 00100<br />
                                            Kenya
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="p-6 bg-gradient-to-br from-primary/10 to-secondary/10 rounded-2xl">
                            <h3 className="font-bold text-lg mb-2">Business Inquiries</h3>
                            <p className="text-slate-600 dark:text-slate-400 mb-4">
                                Interested in partnering with us or have a business proposal?
                            </p>
                            <a href="mailto:business@worldtour.com" className="text-primary font-bold hover:underline">
                                business@worldtour.com
                            </a>
                        </div>
                    </div>

                    {/* Contact Form */}
                    <div className="glass-card p-8 rounded-2xl">
                        <h2 className="text-2xl font-bold mb-6">Send us a Message</h2>

                        {submitted && (
                            <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-800 dark:text-green-200">
                                ✓ Message sent successfully! We'll get back to you soon.
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-sm font-bold mb-2">Name</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 focus:border-primary outline-none transition-colors"
                                    placeholder="Your name"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold mb-2">Email</label>
                                <input
                                    type="email"
                                    required
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 focus:border-primary outline-none transition-colors"
                                    placeholder="your@email.com"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold mb-2">Subject</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.subject}
                                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                                    className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 focus:border-primary outline-none transition-colors"
                                    placeholder="How can we help?"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold mb-2">Message</label>
                                <textarea
                                    required
                                    rows={5}
                                    value={formData.message}
                                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                                    className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 focus:border-primary outline-none transition-colors resize-none"
                                    placeholder="Tell us more..."
                                />
                            </div>

                            <button
                                type="submit"
                                className="w-full py-4 bg-gradient-to-r from-primary to-secondary text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2"
                            >
                                <Send className="w-5 h-5" />
                                Send Message
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
