import React, { useState, useEffect } from 'react';
import { historyApi } from '../../api/client';
import type { SessionHistoryItem, SessionHistoryDetail } from '../../types';

const HistoryView: React.FC = () => {
    const [sessions, setSessions] = useState<SessionHistoryItem[]>([]);
    const [selectedSession, setSelectedSession] = useState<SessionHistoryDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isLoadingDetail, setIsLoadingDetail] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await historyApi.getHistory();
            setSessions(data.sessions);
        } catch (err) {
            console.error("Failed to load history:", err);
            setError("Failed to load history");
        } finally {
            setIsLoading(false);
        }
    };

    const loadSessionDetail = async (sessionId: string) => {
        setIsLoadingDetail(true);
        try {
            const data = await historyApi.getSessionDetail(sessionId);
            setSelectedSession(data);
        } catch (err) {
            console.error("Failed to load session detail:", err);
            setError("Failed to load session details");
        } finally {
            setIsLoadingDetail(false);
        }
    };

    const handleDeleteSession = async (sessionId: string) => {
        if (!confirm("Are you sure you want to delete this session?")) return;
        try {
            await historyApi.deleteSession(sessionId);
            setSessions(prev => prev.filter(s => s.session_id !== sessionId));
            if (selectedSession?.session_id === sessionId) {
                setSelectedSession(null);
            }
        } catch (err) {
            console.error("Failed to delete session:", err);
            setError("Failed to delete session");
        }
    };

    const formatDate = (timestamp: string) => {
        return new Date(timestamp).toLocaleString();
    };

    if (isLoading) {
        return (
            <div className="max-w-4xl mx-auto p-4">
                <div className="text-center text-gray-500">Loading history...</div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-4">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Conversation History</h2>

            {error && (
                <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
                    {error}
                </div>
            )}

            {sessions.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                    <div className="text-gray-400 text-6xl mb-4">📝</div>
                    <h3 className="text-lg font-medium text-gray-600 mb-2">No conversations yet</h3>
                    <p className="text-gray-500">Complete a practice session to see it here.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Session List */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider">Sessions</h3>
                        {sessions.map(session => (
                            <div
                                key={session.session_id}
                                className={`p-4 bg-white rounded-lg shadow-sm border-2 cursor-pointer transition hover:shadow-md ${selectedSession?.session_id === session.session_id
                                        ? 'border-blue-500'
                                        : 'border-transparent'
                                    }`}
                                onClick={() => loadSessionDetail(session.session_id)}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-sm text-gray-500">{formatDate(session.timestamp)}</span>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleDeleteSession(session.session_id);
                                        }}
                                        className="text-red-400 hover:text-red-600 text-sm"
                                    >
                                        Delete
                                    </button>
                                </div>
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="text-sm font-medium">{session.target_language}</span>
                                    <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{session.proficiency_level}</span>
                                    <span className="text-xs text-gray-500">{session.turn_count} turns</span>
                                </div>
                                <p className="text-sm text-gray-600 line-clamp-2">{session.summary}</p>
                            </div>
                        ))}
                    </div>

                    {/* Session Detail */}
                    <div className="lg:sticky lg:top-4">
                        {isLoadingDetail ? (
                            <div className="bg-white rounded-lg shadow-sm p-6 text-center text-gray-500">
                                Loading session details...
                            </div>
                        ) : selectedSession ? (
                            <div className="bg-white rounded-lg shadow-sm p-6 space-y-4 max-h-[80vh] overflow-y-auto">
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-2">Summary</h3>
                                    <p className="text-gray-700">{selectedSession.summary}</p>
                                </div>

                                <hr />

                                <div>
                                    <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-3">Conversation</h3>
                                    <div className="space-y-3">
                                        {selectedSession.turns.map((turn, idx) => (
                                            <div
                                                key={idx}
                                                className={`p-3 rounded-lg ${turn.role === 'user'
                                                        ? 'bg-blue-50 text-blue-900 ml-8'
                                                        : turn.role === 'system'
                                                            ? 'bg-yellow-50 text-yellow-800 text-xs italic'
                                                            : 'bg-gray-50 text-gray-900 mr-8'
                                                    }`}
                                            >
                                                <span className="text-xs font-medium uppercase text-gray-400 block mb-1">
                                                    {turn.role}
                                                </span>
                                                {turn.text}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {selectedSession.feedback.length > 0 && (
                                    <>
                                        <hr />
                                        <div>
                                            <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-3">Feedback</h3>
                                            <div className="space-y-4">
                                                {selectedSession.feedback.map((fb, idx) => (
                                                    <div key={idx} className="bg-gray-50 p-3 rounded-lg">
                                                        <div className="mb-2">
                                                            <span className="text-sm text-red-600 line-through">{fb.original_sentence}</span>
                                                        </div>
                                                        <div className="mb-2">
                                                            <span className="text-sm text-green-600">{fb.corrected_sentence}</span>
                                                        </div>
                                                        <p className="text-xs text-gray-600">{fb.explanation}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </>
                                )}
                            </div>
                        ) : (
                            <div className="bg-white rounded-lg shadow-sm p-6 text-center text-gray-400">
                                Select a session to view details
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default HistoryView;
