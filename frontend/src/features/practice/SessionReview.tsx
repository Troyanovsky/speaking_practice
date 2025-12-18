import React from 'react';
import type { SessionAnalysis, Feedback } from '../../types';

interface SessionReviewProps {
    analysis: SessionAnalysis;
    onClose: () => void;
}

const FeedbackItem: React.FC<{ item: Feedback; index: number }> = ({ item, index }) => {
    return (
        <div className="mb-6 p-4 bg-white rounded-lg shadow-sm border border-gray-100">
            <h3 className="font-semibold text-gray-700 mb-2">Turn {index + 1}</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                <div className="p-3 bg-red-50 rounded-md border border-red-100">
                    <span className="text-xs font-bold text-red-600 uppercase tracking-wide block mb-1">
                        You Said
                    </span>
                    <p className="text-gray-800">{item.original_sentence}</p>
                </div>

                <div className="p-3 bg-green-50 rounded-md border border-green-100">
                    <span className="text-xs font-bold text-green-600 uppercase tracking-wide block mb-1">
                        Better
                    </span>
                    <p className="text-gray-800">{item.corrected_sentence}</p>
                </div>
            </div>

            <div className="ml-1">
                <span className="text-sm font-medium text-gray-500">Explanation: </span>
                <span className="text-sm text-gray-700">{item.explanation}</span>
            </div>
        </div>
    );
};

const SessionReview: React.FC<SessionReviewProps> = ({ analysis, onClose }) => {
    return (
        <div className="flex flex-col h-full bg-gray-50 overflow-y-auto">
            <div className="max-w-3xl mx-auto w-full p-4 space-y-6">
                <header className="text-center py-6">
                    <h1 className="text-3xl font-bold text-gray-800">Session Review</h1>
                    <p className="text-gray-600 mt-2">Here's how you did</p>
                </header>

                {/* Summary Section */}
                <section className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-blue-500">
                    <h2 className="text-xl font-bold text-gray-800 mb-3">Summary</h2>
                    <p className="text-gray-700 leading-relaxed">
                        {analysis.summary}
                    </p>
                </section>

                {/* Feedback Section */}
                <section>
                    <h2 className="text-xl font-bold text-gray-800 mb-4 px-1">Detailed Feedback</h2>
                    <div className="space-y-4">
                        {analysis.feedback.map((item, index) => (
                            <FeedbackItem key={index} item={item} index={index} />
                        ))}
                    </div>
                </section>

                <div className="py-8 flex justify-center">
                    <button
                        onClick={onClose}
                        className="bg-blue-600 text-white px-8 py-3 rounded-full hover:bg-blue-700 transition shadow-md font-medium text-lg"
                    >
                        Start New Session
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SessionReview;
