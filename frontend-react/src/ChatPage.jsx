import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Send, Loader2, Bot, User, FileText, X, Download, Mic, RotateCcw } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const API_URL = 'http://127.0.0.1:8000';

const ChatPage = ({ user }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Greetings. I am the Legal Aid Assistant. How may I assist you with your legal queries today?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const messagesEndRef = useRef(null);

    // Document Generation State
    const [showDocModal, setShowDocModal] = useState(false);
    const [templates, setTemplates] = useState([]);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    const [formData, setFormData] = useState({});
    const [generatingDoc, setGeneratingDoc] = useState(false);
    const [generatedDocUrl, setGeneratedDocUrl] = useState(null);

    // Voice Chat State
    const [showVoiceModal, setShowVoiceModal] = useState(false);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Load session history if session_id is passed
    useEffect(() => {
        const loadSession = async () => {
            if (location.state?.session_id) {
                setCurrentSessionId(location.state.session_id);
                try {
                    const response = await fetch(`${API_URL}/chat/session/${location.state.session_id}`);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.messages && data.messages.length > 0) {
                            setMessages(data.messages);

                            // Restore context to backend
                            if (user?.email) {
                                await fetch(`${API_URL}/chat/restore`, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                        user_id: user.email,
                                        messages: data.messages
                                    })
                                });
                            }
                        }
                    }
                } catch (error) {
                    console.error("Failed to load session:", error);
                }
            }
        };
        loadSession();
    }, [location.state, user]);

    useEffect(() => {
        if (showDocModal) {
            fetchTemplates();
        }
    }, [showDocModal]);

    const fetchTemplates = async () => {
        try {
            const response = await fetch(`${API_URL}/templates`);
            const data = await response.json();
            setTemplates(data.templates || []);
        } catch (error) {
            console.error("Error fetching templates:", error);
        }
    };

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
                body: JSON.stringify({
                    user_query: userMessage.content,
                    user_id: user?.email || "default_user"
                }),
            });

            if (response.ok) {
                const data = await response.json();
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

    const handleSaveAndExit = async () => {
        if (user?.email) {
            try {
                await fetch(`${API_URL}/chat/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: user.email,
                        session_id: currentSessionId
                    }),
                });
            } catch (error) {
                console.error("Failed to save chat:", error);
            }
        }
        navigate('/home');
    };

    const handleNewSession = async () => {
        if (!user?.email) return;

        if (window.confirm("Are you sure you want to start a new session? Current chat history will be saved.")) {
            try {
                // 1. Save current session
                await fetch(`${API_URL}/chat/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: user.email,
                        session_id: currentSessionId
                    }),
                });

                // 2. Start new session
                await fetch(`${API_URL}/chat/new`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: user.email }),
                });

                // 3. Reset UI
                setMessages([
                    { role: 'assistant', content: 'Greetings. I am the Legal Aid Assistant. How may I assist you with your legal queries today?' }
                ]);
                setGeneratedDocUrl(null);
                setSelectedTemplate(null);
            } catch (error) {
                console.error("Error starting new session:", error);
            }
        }
    };

    const handleTemplateSelect = (template) => {
        setSelectedTemplate(template);
        setFormData({});
        setGeneratedDocUrl(null);
    };

    const handleInputChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleGenerateDocument = async () => {
        if (!selectedTemplate) return;
        setGeneratingDoc(true);
        try {
            const response = await fetch(`${API_URL}/document/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_name: selectedTemplate.id,
                    user_inputs: formData,
                    user_query: "Generate document based on inputs"
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setGeneratedDocUrl(data.pdf_url);
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: `I have generated the ${selectedTemplate.title} for you. You can download it from the modal.`
                }]);
            } else {
                alert("Failed to generate document.");
            }
        } catch (error) {
            console.error("Error generating document:", error);
            alert("Error generating document.");
        } finally {
            setGeneratingDoc(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full max-w-4xl h-[85vh] bg-white border border-legal-border rounded-2xl flex flex-col overflow-hidden shadow-2xl relative"
        >
            {/* Header */}
            <div className="p-4 border-b border-legal-border flex items-center justify-between bg-legal-bg">
                <div className="flex items-center gap-4">
                    <button
                        onClick={handleSaveAndExit}
                        className="p-2 hover:bg-white rounded-lg transition-colors text-legal-muted hover:text-legal-navy flex items-center gap-2"
                        title="Save & Exit"
                    >
                        <ArrowLeft size={20} />
                        <span className="text-sm font-medium">Save & Exit</span>
                    </button>
                    <div>
                        <h1 className="font-serif font-bold text-legal-navy">Active Session</h1>
                        <p className="text-xs text-legal-muted flex items-center gap-2">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            Connected to Legal Aid Core
                        </p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={handleNewSession}
                        className="flex items-center gap-2 px-3 py-1.5 bg-legal-navy/10 text-legal-navy border border-legal-navy/20 rounded-lg hover:bg-legal-navy/20 transition-all text-sm"
                        title="Start New Session"
                    >
                        <RotateCcw size={16} />
                        New Session
                    </button>
                    <button
                        onClick={() => setShowVoiceModal(true)}
                        className="flex items-center gap-2 px-3 py-1.5 bg-legal-navy/10 text-legal-navy border border-legal-navy/20 rounded-lg hover:bg-legal-navy/20 transition-all text-sm"
                    >
                        <Mic size={16} />
                        Voice Mode
                    </button>
                    <button
                        onClick={() => setShowDocModal(true)}
                        className="flex items-center gap-2 px-3 py-1.5 bg-legal-navy/10 text-legal-navy border border-legal-navy/20 rounded-lg hover:bg-legal-navy/20 transition-all text-sm"
                    >
                        <FileText size={16} />
                        Generate Doc
                    </button>
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
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-legal-navy text-white' : 'bg-legal-gold/20 text-legal-gold'
                            }`}>
                            {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                        </div>

                        <div className={`max-w-[80%] p-3 rounded-xl text-sm leading-relaxed ${msg.role === 'user'
                            ? 'bg-legal-navy text-white rounded-tr-none shadow-sm'
                            : 'bg-legal-bg border border-legal-border text-legal-text rounded-tl-none shadow-sm'
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
                        <div className="w-8 h-8 bg-legal-gold/20 text-legal-gold rounded-lg flex items-center justify-center shrink-0">
                            <Bot size={18} />
                        </div>
                        <div className="bg-legal-bg border border-legal-border p-3 rounded-xl rounded-tl-none flex items-center gap-2 shadow-sm">
                            <Loader2 size={16} className="animate-spin text-legal-navy" />
                            <span className="text-xs text-legal-muted font-mono">Analyzing legal precedents...</span>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={handleSend} className="p-4 border-t border-legal-border bg-legal-bg">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your legal query..."
                        className="flex-1 bg-white border border-legal-border rounded-lg px-4 py-3 text-legal-text focus:outline-none focus:border-legal-navy placeholder-legal-muted shadow-sm"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim()}
                        className="px-6 py-2 bg-legal-navy text-white rounded-lg font-bold hover:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 shadow-md"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </form>

            {/* Document Generation Modal */}
            <AnimatePresence>
                {showDocModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white border border-legal-border rounded-2xl w-full max-w-2xl max-h-[90%] flex flex-col shadow-2xl"
                        >
                            <div className="p-4 border-b border-legal-border flex justify-between items-center bg-legal-bg rounded-t-2xl">
                                <h2 className="text-lg font-bold text-legal-navy flex items-center gap-2">
                                    <FileText className="text-legal-gold" size={20} />
                                    Generate Legal Document
                                </h2>
                                <button
                                    onClick={() => setShowDocModal(false)}
                                    className="text-legal-muted hover:text-legal-text transition-colors"
                                >
                                    <X size={20} />
                                </button>
                            </div>

                            <div className="flex-1 overflow-hidden flex">
                                {/* Template List */}
                                <div className="w-1/3 border-r border-legal-border overflow-y-auto p-2 bg-legal-bg">
                                    <h3 className="text-xs font-mono text-legal-muted mb-2 px-2 uppercase">Templates</h3>
                                    <div className="space-y-1">
                                        {templates.map(template => (
                                            <button
                                                key={template.id}
                                                onClick={() => handleTemplateSelect(template)}
                                                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${selectedTemplate?.id === template.id
                                                    ? 'bg-legal-navy/10 text-legal-navy border border-legal-navy/20'
                                                    : 'text-legal-muted hover:bg-white hover:text-legal-text'
                                                    }`}
                                            >
                                                {template.title}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Form Area */}
                                <div className="flex-1 p-6 overflow-y-auto">
                                    {selectedTemplate ? (
                                        <div className="space-y-4">
                                            <h3 className="text-xl font-bold text-legal-navy mb-4">{selectedTemplate.title}</h3>

                                            {Object.entries(selectedTemplate.fields).map(([key, label]) => (
                                                <div key={key} className="space-y-1">
                                                    <label className="text-xs text-legal-muted uppercase font-bold">{label}</label>
                                                    <input
                                                        type="text"
                                                        value={formData[key] || ''}
                                                        onChange={(e) => handleInputChange(key, e.target.value)}
                                                        className="w-full bg-white border border-legal-border rounded-lg px-3 py-2 text-legal-text focus:outline-none focus:border-legal-navy"
                                                        placeholder={`Enter ${label}...`}
                                                    />
                                                </div>
                                            ))}

                                            <div className="pt-4 flex gap-3">
                                                <button
                                                    onClick={handleGenerateDocument}
                                                    disabled={generatingDoc}
                                                    className="flex-1 bg-legal-navy text-white font-bold py-2 rounded-lg hover:bg-blue-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-md"
                                                >
                                                    {generatingDoc ? (
                                                        <>
                                                            <Loader2 size={18} className="animate-spin" />
                                                            Generating...
                                                        </>
                                                    ) : (
                                                        <>
                                                            <FileText size={18} />
                                                            Generate PDF
                                                        </>
                                                    )}
                                                </button>

                                                {generatedDocUrl && (
                                                    <a
                                                        href={generatedDocUrl}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="px-4 py-2 bg-green-50 text-green-600 border border-green-200 rounded-lg hover:bg-green-100 transition-colors flex items-center gap-2"
                                                    >
                                                        <Download size={18} />
                                                        Download
                                                    </a>
                                                )}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-2">
                                            <FileText size={48} className="opacity-20" />
                                            <p>Select a template to start drafting</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Voice Chat Modal */}
            <AnimatePresence>
                {showVoiceModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white border border-legal-border rounded-2xl w-full max-w-md flex flex-col shadow-2xl overflow-hidden"
                        >
                            <div className="p-4 border-b border-legal-border flex justify-between items-center bg-legal-bg">
                                <h2 className="text-lg font-bold text-legal-navy flex items-center gap-2">
                                    <Mic className="text-legal-gold" size={20} />
                                    Voice Assistant
                                </h2>
                                <button
                                    onClick={() => setShowVoiceModal(false)}
                                    className="text-legal-muted hover:text-legal-text transition-colors"
                                >
                                    <X size={20} />
                                </button>
                            </div>
                            <div className="p-4 h-[500px] flex items-center justify-center text-legal-muted">
                                <p>Voice chat feature is currently unavailable.</p>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default ChatPage;
