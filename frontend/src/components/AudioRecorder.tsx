import React, { useState, useRef } from 'react';

interface AudioRecorderProps {
    onRecordingComplete: (file: File) => void;
    disabled?: boolean;
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({ onRecordingComplete, disabled }) => {
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);

            mediaRecorderRef.current.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorderRef.current.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
                const file = new File([blob], 'recording.webm', { type: 'audio/webm' });
                onRecordingComplete(file);
                chunksRef.current = [];
            };

            mediaRecorderRef.current.start();
            setIsRecording(true);
        } catch (err) {
            console.error("Error accessing microphone:", err);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.code === 'Space' && !isRecording && !disabled) {
            startRecording();
        }
    };

    const handleKeyUp = (e: React.KeyboardEvent) => {
        if (e.code === 'Space' && isRecording) {
            stopRecording();
        }
    };

    return (
        <div
            className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
            tabIndex={0}
            onKeyDown={handleKeyDown}
            onKeyUp={handleKeyUp}
        >
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-blue-500'}`}>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
            </div>
            <p className="text-gray-600 font-medium">
                {isRecording ? "Release Space to Send" : "Hold Space to Speak"}
            </p>
            {disabled && <p className="text-xs text-red-400 mt-2">Session ended or processing...</p>}
        </div>
    );
};

export default AudioRecorder;
