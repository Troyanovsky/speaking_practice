import React from 'react';
import { useNotification } from './NotificationContext';

const Notification: React.FC = () => {
    const { notifications, removeNotification } = useNotification();

    if (notifications.length === 0) return null;

    return (
        <div className="fixed top-4 right-4 z-50 flex flex-col space-y-2 pointer-events-none">
            {notifications.map((n) => (
                <div
                    key={n.id}
                    className={`px-4 py-3 rounded-lg shadow-lg text-white font-medium flex items-center justify-between min-w-[300px] pointer-events-auto transition-all duration-300 transform translate-x-0 animate-scale-in ${n.type === 'error' ? 'bg-red-500' :
                            n.type === 'success' ? 'bg-green-500' :
                                n.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                        }`}
                >
                    <span>{n.message}</span>
                    <button
                        onClick={() => removeNotification(n.id)}
                        className="ml-4 text-white hover:text-gray-200 focus:outline-none"
                    >
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            ))}
        </div>
    );
};

export default Notification;
