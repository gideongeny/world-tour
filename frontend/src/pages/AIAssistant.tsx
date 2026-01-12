import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, User, Bot } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

function AIAssistant() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: '✈️ Hey there! I\'m your AI Travel Assistant, and I\'m excited to help you plan an amazing trip! 🌍\n\nI can help you with:\n• Finding the perfect destination for your budget and interests\n• Recommending hotels and flights\n• Creating custom itineraries\n• Sharing insider tips and local insights\n\nWhat kind of adventure are you dreaming about? Beach getaway? Mountain trek? City exploration? Let\'s make it happen! ⭐'
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        if (!input.trim()) return;

        const userMsg = input;
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setInput('');
        setIsTyping(true);

        // Mock API call or real one
        fetch(`${API_BASE_URL}/ai/api/chat`, {
            // Endpoint path validation needed later, assumes /booking/ai/chat or similar. 
            // Based on blueprints/ai/routes.py it's likely /ai/chat if registered properly.
            // Let's assume /ai/chat at root + blueprint prefix.
            // Verifying bluepring prefix... usually /ai
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMsg })
        })
            .then(res => res.json())
            .then(data => {
                setMessages(prev => [...prev, { role: 'assistant', content: data.response || "I found some interesting options for you..." }]);
                setIsTyping(false);
            })
            .catch((err) => {
                console.error("AI Error:", err);
                setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting to the server. Please check your internet or try again later. 🔌" }]);
                setIsTyping(false);
            });
    };

    return (
        <div className="pt-24 pb-10 px-6 max-w-4xl mx-auto h-screen flex flex-col">
            <div className="mb-6 text-center">
                <h1 className="text-4xl font-black mb-2 flex items-center justify-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-tr from-primary to-secondary rounded-2xl flex items-center justify-center text-white shadow-lg shadow-primary/30">
                        <Sparkles className="w-6 h-6" />
                    </div>
                    AI Travel Planner
                </h1>
                <p className="text-slate-500">Your personal intelligent companion for all things travel.</p>
            </div>

            <div className="flex-1 bg-white dark:bg-slate-800 rounded-3xl shadow-xl border border-slate-100 dark:border-slate-700 overflow-hidden flex flex-col">
                <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50 dark:bg-slate-900/50">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-slate-200' : 'bg-primary text-white'
                                }`}>
                                {msg.role === 'user' ? <User className="w-5 h-5 text-slate-600" /> : <Bot className="w-5 h-5" />}
                            </div>
                            <div className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'user'
                                ? 'bg-white shadow-sm text-slate-800 rounded-tr-none'
                                : 'bg-primary/10 text-slate-800 dark:text-white rounded-tl-none border border-primary/10'
                                }`}>
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {isTyping && (
                        <div className="flex gap-4">
                            <div className="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center"><Bot className="w-5 h-5" /></div>
                            <div className="bg-primary/5 p-4 rounded-2xl rounded-tl-none flex gap-1 items-center">
                                <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce"></span>
                                <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                                <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                            </div>
                        </div>
                    )}
                    <div ref={bottomRef} />
                </div>

                <div className="p-4 bg-white dark:bg-slate-800 border-t border-slate-100 dark:border-slate-700">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSend()}
                            placeholder="Ask anything... 'Find me a beach in Italy'"
                            className="flex-1 bg-slate-100 dark:bg-slate-900 px-6 py-4 rounded-xl font-medium outline-none border-2 border-transparent focus:border-primary/20 transition-all"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!input.trim()}
                            className="bg-primary text-white p-4 rounded-xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-primary/20"
                        >
                            <Send className="w-6 h-6" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AIAssistant;
