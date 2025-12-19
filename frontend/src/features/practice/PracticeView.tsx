import React, { useState, useEffect, useRef } from 'react';
import { sessionApi, settingsApi } from '../../api/client';
import type { Turn, SessionCreate, SessionAnalysis } from '../../types';
import AudioRecorder from '../../components/AudioRecorder';
import SessionReview from './SessionReview';

// Supported languages from PRD
const LANGUAGES = ['English', 'Spanish', 'French', 'Italian', 'Portuguese'];
const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

const PracticeView: React.FC = () => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [turns, setTurns] = useState<Turn[]>([]);
    const [isActive, setIsActive] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [analysis, setAnalysis] = useState<SessionAnalysis | null>(null);
    const [isSessionEnding, setIsSessionEnding] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // User-configurable language settings
    const [primaryLanguage, setPrimaryLanguage] = useState('English');
    const [targetLanguage, setTargetLanguage] = useState('Spanish');

    const [proficiencyLevel, setProficiencyLevel] = useState('A1');
    const [stopWord, setStopWord] = useState('stop session');

    // Load defaults from backend settings
    useEffect(() => {
        const loadDefaults = async () => {
            try {
                const settings = await settingsApi.getSettings();
                setPrimaryLanguage(settings.primary_language);
                setTargetLanguage(settings.target_language);
                setProficiencyLevel(settings.proficiency_level);
                setStopWord(settings.stop_word);
            } catch (error) {
                console.error("Failed to load settings defaults:", error);
            }
        };
        loadDefaults();
    }, []);

    const startSession = async () => {
        setIsLoading(true);
        setAnalysis(null);
        setIsSessionEnding(false);
        try {
            const settings: SessionCreate = {
                primary_language: primaryLanguage,
                target_language: targetLanguage,
                proficiency_level: proficiencyLevel,
                stop_word: stopWord
            };
            const data = await sessionApi.startSession(settings);
            setSessionId(data.session_id);
            setTurns(data.turns);
            setIsActive(data.is_active);

            // Play greeting audio if available
            if (data.turns.length > 0) {
                const lastTurn = data.turns[data.turns.length - 1];
                if (lastTurn.audio_url) {
                    const audio = new Audio(lastTurn.audio_url.startsWith('http') ? lastTurn.audio_url : `http://localhost:8000${lastTurn.audio_url}`);
                    audio.play();
                }
            }
        } catch (error) {
            console.error("Failed to start session:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRecordingComplete = async (file: File) => {
        if (!sessionId) return;

        // Add optimistic user turn
        const optimisticTurn: Turn = { role: 'user', text: "Processing audio..." };
        setTurns(prev => [...prev, optimisticTurn]);

        setIsLoading(true);
        try {
            const response = await sessionApi.sendTurn(sessionId, file);

            // Replace optimistic turn and add AI response
            setTurns(prev => {
                const newTurns = prev.slice(0, -1); // Remove optimistic
                newTurns.push({ role: 'user', text: response.user_text });
                newTurns.push({ role: 'system', text: response.ai_text, audio_url: response.ai_audio_url });
                return newTurns;
            });

            // Handle session ending state
            if (response.is_session_ending) {
                setIsSessionEnding(true);
                setIsActive(false);
            }

            // Play audio
            if (response.ai_audio_url) {
                const audio = new Audio(response.ai_audio_url.startsWith('http') ? response.ai_audio_url : `http://localhost:8000${response.ai_audio_url}`);
                await audio.play();
                
                // Only fetch analysis after audio finishes if session ended
                if (response.is_session_ended) {
                    try {
                        const analysisData = await sessionApi.endSession(sessionId);
                        setAnalysis(analysisData);
                        setIsSessionEnding(false);
                    } catch (err) {
                        console.error("Failed to fetch session analysis:", err);
                        setIsSessionEnding(false);
                    }
                }
            } else if (response.is_session_ended) {
                // If no audio, fetch analysis immediately
                try {
                    const analysisData = await sessionApi.endSession(sessionId);
                    setAnalysis(analysisData);
                    setIsSessionEnding(false);
                } catch (err) {
                    console.error("Failed to fetch session analysis:", err);
                    setIsSessionEnding(false);
                }
            }

        } catch (error) {
            console.error("Failed to send turn:", error);
            setTurns(prev => prev.slice(0, -1)); // Remove optimistic on error
        } finally {
            setIsLoading(false);
        }
    };

    const handleCloseReview = () => {
        setSessionId(null);
        setTurns([]);
        setAnalysis(null);
        setIsActive(false);
        setIsSessionEnding(false);
    };

    const stopSession = async () => {
        if (!sessionId) return;
        
        setIsLoading(true);
        try {
            const response = await sessionApi.stopSession(sessionId);
            setIsSessionEnding(true);
            setIsActive(false);
            
            // Add AI response to turns
            setTurns(prev => [...prev, { role: 'system', text: response.ai_text, audio_url: response.ai_audio_url }]);
            
            // Play audio
            if (response.ai_audio_url) {
                const audio = new Audio(response.ai_audio_url.startsWith('http') ? response.ai_audio_url : `http://localhost:8000${response.ai_audio_url}`);
                await audio.play();
                
                // Only fetch analysis after audio finishes
                try {
                    const analysisData = await sessionApi.endSession(sessionId);
                    setAnalysis(analysisData);
                    setIsSessionEnding(false);
                } catch (err) {
                    console.error("Failed to fetch session analysis:", err);
                    setIsSessionEnding(false);
                }
            } else {
                // If no audio, fetch analysis immediately
                try {
                    const analysisData = await sessionApi.endSession(sessionId);
                    setAnalysis(analysisData);
                    setIsSessionEnding(false);
                } catch (err) {
                    console.error("Failed to fetch session analysis:", err);
                    setIsSessionEnding(false);
                }
            }
        } catch (error) {
            console.error("Failed to stop session:", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [turns]);

    if (analysis) {
        return <SessionReview analysis={analysis} onClose={handleCloseReview} turns={turns} />;
    }

    return (
        <div className="flex flex-col h-screen max-w-2xl mx-auto p-4 bg-gray-50">
            <header className="mb-4 text-center">
                <h1 className="text-2xl font-bold text-gray-800">Speaking Practice</h1>
            </header>

            <div className="flex-1 overflow-y-auto mb-6 p-4 bg-white rounded-lg shadow-sm" ref={scrollRef}>
                {turns.length === 0 && !sessionId && (
                    <div className="flex flex-col justify-center items-center h-full space-y-6">
                        {/* Language Settings */}
                        <div className="w-full max-w-md space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Your Primary Language
                                </label>
                                <select
                                    value={primaryLanguage}
                                    onChange={(e) => setPrimaryLanguage(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                >
                                    {LANGUAGES.map(lang => (
                                        <option key={lang} value={lang}>{lang}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Language to Practice
                                </label>
                                <select
                                    value={targetLanguage}
                                    onChange={(e) => setTargetLanguage(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                >
                                    {LANGUAGES.map(lang => (
                                        <option key={lang} value={lang}>{lang}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Proficiency Level (CEFR)
                                </label>
                                <select
                                    value={proficiencyLevel}
                                    onChange={(e) => setProficiencyLevel(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                >
                                    {CEFR_LEVELS.map(level => (
                                        <option key={level} value={level}>{level}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Stop Word
                                </label>
                                <input
                                    type="text"
                                    value={stopWord}
                                    onChange={(e) => setStopWord(e.target.value)}
                                    placeholder="e.g. stop session"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                                <p className="mt-1 text-xs text-gray-500">
                                    Say this phrase during practice to end the session.
                                </p>
                            </div>
                        </div>

                        <button
                            onClick={startSession}
                            disabled={isLoading}
                            className="bg-blue-600 text-white px-6 py-3 rounded-full hover:bg-blue-700 transition disabled:opacity-50"
                        >
                            {isLoading ? "Starting..." : "Start New Session"}
                        </button>
                    </div>
                )}

                {/* Active session: show waveform with turn counter instead of chat history */}
                {sessionId && isActive && (
                    <div className="flex flex-col justify-center items-center h-full space-y-8">
                        <div className="text-center">
                            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Session in Progress</h2>
                            <p className="text-gray-600">Focus on your conversation with the AI</p>
                        </div>
                        
                        {/* Waveform visualization */}
                        <div className="w-full max-w-md">
                            <div className="flex items-center justify-center space-x-1">
                                {[...Array(20)].map((_, i) => (
                                    <div
                                        key={i}
                                        className="bg-blue-500 rounded-full animate-pulse"
                                        style={{
                                            width: '4px',
                                            height: `${20 + Math.sin(i * 0.5) * 15}px`,
                                            animationDelay: `${i * 0.1}s`
                                        }}
                                    />
                                ))}
                            </div>
                        </div>
                        
                        {/* Turn counter */}
                        <div className="text-center">
                            <div className="text-3xl font-bold text-blue-600">
                                {Math.floor(turns.length / 2)}/15
                            </div>
                            <p className="text-sm text-gray-500 mt-1">Turns completed</p>
                        </div>
                        
                        {/* Stop Session Button */}
                        <button
                            onClick={stopSession}
                            disabled={isLoading}
                            className="bg-red-600 text-white px-6 py-2 rounded-full hover:bg-red-700 transition disabled:opacity-50 flex items-center space-x-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <rect x="6" y="6" width="12" height="12" strokeWidth="2" rx="2"/>
                            </svg>
                            <span>{isLoading ? "Stopping..." : "Stop Session"}</span>
                        </button>
                        
                        <div className="text-center max-w-sm">
                            <p className="text-xs text-gray-400">
                                Chat history will be available at the end of the session
                            </p>
                        </div>
                    </div>
                )}

                {/* Session ending - waiting for final audio to play */}
                {isSessionEnding && (
                    <div className="flex flex-col justify-center items-center h-full space-y-6">
                        <div className="text-center">
                            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Session Ending</h2>
                            <p className="text-gray-600">Please wait for the final response...</p>
                        </div>
                        
                        <div className="animate-pulse flex space-x-2">
                            <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                            <div className="w-3 h-3 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                            <div className="w-3 h-3 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                        
                        <div className="text-center max-w-sm">
                            <p className="text-xs text-gray-400">
                                Your session summary will appear after the response finishes
                            </p>
                        </div>
                    </div>
                )}

                {/* Session ended but not showing analysis yet */}
                {sessionId && !isActive && !analysis && !isSessionEnding && (
                    <div className="flex flex-col justify-center items-center h-full space-y-6">
                        <div className="text-center">
                            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Session Ended</h2>
                            <p className="text-gray-600">Generating your session analysis...</p>
                        </div>
                        
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    </div>
                )}
            </div>

            {sessionId && !analysis && (
                <div className="bg-white p-4 rounded-lg shadow-sm">
                    <AudioRecorder onRecordingComplete={handleRecordingComplete} disabled={!isActive || isLoading || isSessionEnding} />
                </div>
            )}
        </div>
    );
};

export default PracticeView;
