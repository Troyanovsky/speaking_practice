export interface Turn {
    role: 'user' | 'system';
    text: string;
    audio_url?: string;
}

export interface SessionCreate {
    primary_language: string;
    target_language: string;
    proficiency_level: string;
}

export interface SessionResponse {
    session_id: string;
    turns: Turn[];
    is_active: boolean;
}

export interface TurnResponse {
    user_text: string;
    ai_text: string;
    ai_audio_url: string;
    is_session_ended: boolean;
}

export interface Feedback {
    original_sentence: string;
    corrected_sentence: string;
    explanation: string;
}

export interface SessionAnalysis {
    summary: string;
    feedback: Feedback[];
}
