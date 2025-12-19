import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const message = error.response?.data?.message || error.message || 'An unexpected error occurred';
        // We'll use a custom event or a similar mechanism since we can't use hooks here easily
        // Or better, let's export a function to set a dispatcher
        if (apiErrorHandler) {
            apiErrorHandler(message);
        }
        return Promise.reject(error);
    }
);

let apiErrorHandler: ((message: string) => void) | null = null;

export const setApiErrorHandler = (handler: (message: string) => void) => {
    apiErrorHandler = handler;
};

export const sessionApi = {
    startSession: async (data: { primary_language: string, target_language: string, proficiency_level: string }) => {
        const response = await api.post('/session/start', data);
        return response.data;
    },
    sendTurn: async (sessionId: string, audioFile: File) => {
        const formData = new FormData();
        formData.append('audio', audioFile);
        const response = await api.post(`/session/${sessionId}/turn`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },
    endSession: async (sessionId: string) => {
        const response = await api.post(`/session/${sessionId}/end`);
        return response.data;
    }
};

export const settingsApi = {
    getSettings: async () => {
        const response = await api.get('/settings/');
        return response.data;
    },
    updateSettings: async (settings: any) => {
        const response = await api.post('/settings/', settings);
        return response.data;
    }
};

export const historyApi = {
    getHistory: async () => {
        const response = await api.get('/history/');
        return response.data;
    },
    getSessionDetail: async (sessionId: string) => {
        const response = await api.get(`/history/${sessionId}`);
        return response.data;
    },
    deleteSession: async (sessionId: string) => {
        const response = await api.delete(`/history/${sessionId}`);
        return response.data;
    }
};

