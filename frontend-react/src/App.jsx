import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Square, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import HomePage from './HomePage';
import ChatPage from './ChatPage';

const API_URL = 'http://127.0.0.1:8000';

const ParticleNetwork = () => {
    const canvasRef = useRef(null);
    const mouseRef = useRef({ x: 0, y: 0 });

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        let animationFrameId;

        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const particles = [];
        const particleCount = 200;
        const connectionDistance = 120;
        const mouseDistance = 200;

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.size = Math.random() * 2 + 1;
                this.baseX = this.x;
                this.baseY = this.y;
                this.density = (Math.random() * 30) + 1;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;

                let dx = mouseRef.current.x - this.x;
                let dy = mouseRef.current.y - this.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                let forceDirectionX = dx / distance;
                let forceDirectionY = dy / distance;
                let maxDistance = mouseDistance;
                let force = (maxDistance - distance) / maxDistance;
                let directionX = forceDirectionX * force * this.density;
                let directionY = forceDirectionY * force * this.density;

                if (distance < mouseDistance) {
                    this.x -= directionX;
                    this.y -= directionY;
                } else {
                    if (this.x !== this.baseX) {
                        let dx = this.x - this.baseX;
                        this.x -= dx / 10;
                    }
                    if (this.y !== this.baseY) {
                        let dy = this.y - this.baseY;
                        this.y -= dy / 10;
                    }
                }
            }

            draw() {
                ctx.fillStyle = '#00ff9d';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.closePath();
                ctx.fill();
            }
        }

        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();

                for (let j = i; j < particles.length; j++) {
                    let dx = particles[i].x - particles[j].x;
                    let dy = particles[i].y - particles[j].y;
                    let distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < connectionDistance) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(0, 255, 157, ${1 - distance / connectionDistance})`;
                        ctx.lineWidth = 1;
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
            animationFrameId = requestAnimationFrame(animate);
        };

        animate();

        const handleMouseMove = (event) => {
            mouseRef.current.x = event.x;
            mouseRef.current.y = event.y;
        };

        window.addEventListener('mousemove', handleMouseMove);

        return () => {
            window.removeEventListener('resize', resizeCanvas);
            window.removeEventListener('mousemove', handleMouseMove);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return <canvas ref={canvasRef} className="fixed top-0 left-0 w-full h-full -z-10 bg-cyber-dark" />;
};

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
            className="relative w-full max-w-md p-8 rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 shadow-2xl"
        >
            <div className="flex flex-col items-center mb-8">
                <div className="w-12 h-12 bg-cyber-green/20 rounded-lg flex items-center justify-center mb-4 shadow-[0_0_15px_rgba(0,255,157,0.3)]">
                    <Square className="w-6 h-6 text-cyber-green" />
                </div>
                <h1 className="text-3xl font-mono font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyber-green to-cyber-teal drop-shadow-[0_0_10px_rgba(0,255,157,0.5)]">
                    LEGAL AID CHATBOT
                </h1>
                <p className="text-gray-400 text-sm mt-2 font-mono italic">
                    "Justice never sleeps, and neither do I."
                </p>
            </div>

            <div className="flex p-1 bg-black/20 rounded-lg mb-6">
                <button
                    onClick={() => setIsLogin(true)}
                    className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-300 ${isLogin ? 'bg-cyber-green/20 text-cyber-green shadow-sm' : 'text-gray-400 hover:text-white'
                        }`}
                >
                    LOGIN
                </button>
                <button
                    onClick={() => setIsLogin(false)}
                    className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-300 ${!isLogin ? 'bg-cyber-green/20 text-cyber-green shadow-sm' : 'text-gray-400 hover:text-white'
                        }`}
                >
                    SIGN UP
                </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && (
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <label className="block text-xs font-mono text-cyber-green mb-1 ml-1">FIRST NAME</label>
                            <input
                                type="text"
                                required
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-cyber-green/50 focus:ring-1 focus:ring-cyber-green/50 transition-all font-mono text-sm"
                                placeholder="John"
                            />
                        </div>
                        <div className="flex-1">
                            <label className="block text-xs font-mono text-cyber-green mb-1 ml-1">LAST NAME</label>
                            <input
                                type="text"
                                required
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-cyber-green/50 focus:ring-1 focus:ring-cyber-green/50 transition-all font-mono text-sm"
                                placeholder="Doe"
                            />
                        </div>
                    </div>
                )}

                <div>
                    <label className="block text-xs font-mono text-cyber-green mb-1 ml-1">EMAIL_ID</label>
                    <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-cyber-green/50 focus:ring-1 focus:ring-cyber-green/50 transition-all font-mono text-sm"
                        placeholder="user@system.net"
                    />
                </div>
                <div>
                    <label className="block text-xs font-mono text-cyber-green mb-1 ml-1">PASSCODE</label>
                    <input
                        type="password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-cyber-green/50 focus:ring-1 focus:ring-cyber-green/50 transition-all font-mono text-sm"
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
                    className="w-full bg-cyber-green hover:bg-emerald-400 text-black font-bold py-3 rounded-lg transition-all duration-300 transform hover:-translate-y-0.5 hover:shadow-[0_0_20px_rgba(0,255,157,0.4)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-6"
                >
                    {loading ? <Loader2 className="animate-spin" size={20} /> : (isLogin ? 'LOGIN' : 'SIGN UP')}
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
            <div className="relative min-h-screen flex items-center justify-center font-sans text-white overflow-hidden">
                <ParticleNetwork />
                <Routes>
                    <Route path="/" element={<LoginPage setUser={setUser} />} />
                    <Route path="/home" element={<HomePage user={user} setUser={setUser} />} />
                    <Route path="/chat" element={<ChatPage />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
