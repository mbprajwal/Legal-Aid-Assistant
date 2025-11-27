import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Send, Loader2, Bot, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_URL = 'http://127.0.0.1:8000';

const ChatPage = () => {
    const navigate = useNavigate();
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Greetings. I am the Legal Aid Assistant. How may I assist you with your legal queries today?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage.content }),
            });

            if (response.ok) {
                const data = await response.json();
                // Assuming the API returns { response: "..." } or similar
                // Adjust based on actual API response structure
                const botResponse = data.response || data.message || JSON.stringify(data);
                setMessages(prev => [...prev, { role: 'assistant', content: botResponse }]);
            } else {
                setMessages(prev => [...prev, { role: 'assistant', content: "Error: Unable to reach the legal database. Please try again later." }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Connection Error: Backend server may be offline." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full max-w-4xl h-[85vh] bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl flex flex-col overflow-hidden shadow-2xl"
        >
            {/* Header */}
            <div className="p-4 border-b border-white/10 flex items-center gap-4 bg-black/20">
                <button
                    onClick={() => navigate('/home')}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white"
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 className="font-mono font-bold text-cyber-green">ACTIVE SESSION</h1>
                    <p className="text-xs text-gray-500 flex items-center gap-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        Connected to Legal Aid Core
                    </p>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 p-6 overflow-y-auto custom-scrollbar space-y-4">
                {messages.map((msg, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-cyber-teal/20 text-cyber-teal' : 'bg-cyber-green/20 text-cyber-green'
                            }`}>
                            {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                        </div>

                        <div className={`max-w-[80%] p-3 rounded-xl text-sm leading-relaxed ${msg.role === 'user'
                                ? 'bg-cyber-teal/10 border border-cyber-teal/20 text-gray-200 rounded-tr-none'
                                : 'bg-white/5 border border-white/10 text-gray-300 rounded-tl-none'
                            }`}>
                            {msg.content}
                        </div>
                    </motion.div>
                ))}

                {loading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex gap-3"
                    >
                        <div className="w-8 h-8 bg-cyber-green/20 text-cyber-green rounded-lg flex items-center justify-center shrink-0">
                            <Bot size={18} />
                        </div>
                        <div className="bg-white/5 border border-white/10 p-3 rounded-xl rounded-tl-none flex items-center gap-2">
                            <Loader2 size={16} className="animate-spin text-cyber-green" />
                            <span className="text-xs text-gray-500 font-mono">ANALYZING LEGAL PRECEDENTS...</span>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={handleSend} className="p-4 border-t border-white/10 bg-black/20">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your legal query..."
                        className="flex-1 bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-cyber-green/50 placeholder-gray-600"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim()}
                        className="px-6 py-2 bg-cyber-green text-black rounded-lg font-bold hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </form>
        </motion.div>
    );
};

export default ChatPage;
