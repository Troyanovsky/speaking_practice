import React, { useState, useEffect, useRef } from 'react';
import { sessionApi, settingsApi } from '../../api/client';
import type { Turn, SessionCreate } from '../../types';
import AudioRecorder from '../../components/AudioRecorder';

// Supported languages from PRD
const LANGUAGES = ['English', 'Spanish', 'French', 'Italian', 'Portuguese'];
const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

const PracticeView: React.FC = () => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [turns, setTurns] = useState<Turn[]>([]);
    const [isActive, setIsActive] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
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

            if (response.is_session_ended) {
                setIsActive(false);
            }

            // Play audio
            if (response.ai_audio_url) {
                const audio = new Audio(response.ai_audio_url.startsWith('http') ? response.ai_audio_url : `http://localhost:8000${response.ai_audio_url}`);
                audio.play();
            }

        } catch (error) {
            console.error("Failed to send turn:", error);
            setTurns(prev => prev.slice(0, -1)); // Remove optimistic on error
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [turns]);

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

                {turns.map((turn, index) => (
                    <div key={index} className={`mb-4 flex ${turn.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-lg p-3 ${turn.role === 'user' ? 'bg-blue-100 text-blue-900' : 'bg-gray-100 text-gray-900'}`}>
                            <p>{turn.text}</p>
                        </div>
                    </div>
                ))}
            </div>

            {sessionId && (
                <div className="bg-white p-4 rounded-lg shadow-sm">
                    <AudioRecorder onRecordingComplete={handleRecordingComplete} disabled={!isActive || isLoading} />
                </div>
            )}
        </div>
    );
};

export default PracticeView;
