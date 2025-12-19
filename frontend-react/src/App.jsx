import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Square, Loader2, AlertCircle, CheckCircle2, Scale } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import HomePage from './HomePage';
import ChatPage from './ChatPage';

const API_URL = 'http://127.0.0.1:8000';



const LoginPage = ({ setUser }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        try {
            const endpoint = isLogin ? '/login' : '/signup';
            const payload = isLogin
                ? { email, password }
                : { email, password, firstName, lastName };

            const response = await fetch(`${API_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage({ type: 'success', text: data.message || (isLogin ? 'Login successful!' : 'Account created!') });

                if (isLogin) {
                    // Use data from backend
                    const userData = {
                        email,
                        firstName: data.firstName || 'User',
                        lastName: data.lastName || ''
                    };
                    setUser(userData);
                    localStorage.setItem('user', JSON.stringify(userData));

                    setTimeout(() => {
                        navigate('/home');
                    }, 1000);
                } else {
                    // On signup, we still have the local state
                    const userData = {
                        email,
                        firstName: firstName || 'User',
                        lastName: lastName || ''
                    };
                    // We don't set user here, we wait for them to login or just redirect to login

                    setTimeout(() => {
                        setIsLogin(true);
                        setMessage(null);
                        setEmail('');
                        setPassword('');
                        setFirstName('');
                        setLastName('');
                    }, 1500);
                }
            } else {
                setMessage({ type: 'error', text: data.detail || 'An error occurred' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to connect to server.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="relative w-full max-w-md p-8 rounded-2xl bg-white shadow-xl border border-legal-border"
        >
            <div className="flex flex-col items-center mb-8">
                <div className="w-16 h-16 bg-legal-navy/10 rounded-full flex items-center justify-center mb-4">
                    <Scale className="w-8 h-8 text-legal-navy" />
                </div>
                <h1 className="text-3xl font-serif font-bold tracking-tight text-legal-navy text-center">
                    Legal Aid Assistant
                </h1>
                <p className="text-legal-muted text-sm mt-2 text-center">
                    Professional legal guidance, simplified.
                </p>
            </div>

            <div className="flex p-1 bg-legal-bg rounded-lg mb-6 border border-legal-border">
                <button
                    onClick={() => setIsLogin(true)}
                    className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-300 ${isLogin ? 'bg-white text-legal-navy shadow-sm' : 'text-legal-muted hover:text-legal-text'
                        }`}
                >
                    Login
                </button>
                <button
                    onClick={() => setIsLogin(false)}
                    className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-300 ${!isLogin ? 'bg-white text-legal-navy shadow-sm' : 'text-legal-muted hover:text-legal-text'
                        }`}
                >
                    Sign Up
                </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && (
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <label className="block text-xs font-bold text-legal-text mb-1 ml-1">First Name</label>
                            <input
                                type="text"
                                required
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                className="w-full bg-legal-bg border border-legal-border rounded-lg px-4 py-3 text-legal-text placeholder-legal-muted focus:outline-none focus:border-legal-navy focus:ring-1 focus:ring-legal-navy transition-all text-sm"
                                placeholder="John"
                            />
                        </div>
                        <div className="flex-1">
                            <label className="block text-xs font-bold text-legal-text mb-1 ml-1">Last Name</label>
                            <input
                                type="text"
                                required
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                className="w-full bg-legal-bg border border-legal-border rounded-lg px-4 py-3 text-legal-text placeholder-legal-muted focus:outline-none focus:border-legal-navy focus:ring-1 focus:ring-legal-navy transition-all text-sm"
                                placeholder="Doe"
                            />
                        </div>
                    </div>
                )}

                <div>
                    <label className="block text-xs font-bold text-legal-text mb-1 ml-1">Email Address</label>
                    <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full bg-legal-bg border border-legal-border rounded-lg px-4 py-3 text-legal-text placeholder-legal-muted focus:outline-none focus:border-legal-navy focus:ring-1 focus:ring-legal-navy transition-all text-sm"
                        placeholder="user@example.com"
                    />
                </div>
                <div>
                    <label className="block text-xs font-bold text-legal-text mb-1 ml-1">Password</label>
                    <input
                        type="password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full bg-legal-bg border border-legal-border rounded-lg px-4 py-3 text-legal-text placeholder-legal-muted focus:outline-none focus:border-legal-navy focus:ring-1 focus:ring-legal-navy transition-all text-sm"
                        placeholder="••••••••"
                    />
                </div>

                <AnimatePresence mode='wait'>
                    {message && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className={`p-3 rounded-lg text-sm flex items-center gap-2 ${message.type === 'error' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-green-500/10 text-green-400 border border-green-500/20'
                                }`}
                        >
                            {message.type === 'error' ? <AlertCircle size={16} /> : <CheckCircle2 size={16} />}
                            {message.text}
                        </motion.div>
                    )}
                </AnimatePresence>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-legal-navy hover:bg-blue-800 text-white font-bold py-3 rounded-lg transition-all duration-300 transform hover:-translate-y-0.5 shadow-lg shadow-blue-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-6"
                >
                    {loading ? <Loader2 className="animate-spin" size={20} /> : (isLogin ? 'Login' : 'Create Account')}
                </button>
            </form>
        </motion.div>
    );
};

function App() {
    const [user, setUser] = useState(null);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    return (
        <Router>
            <div className="relative min-h-screen flex items-center justify-center font-sans text-legal-text overflow-hidden bg-legal-bg">
                <Routes>
                    <Route path="/" element={<LoginPage setUser={setUser} />} />
                    <Route path="/home" element={<HomePage user={user} setUser={setUser} />} />
                    <Route path="/chat" element={<ChatPage user={user} />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
