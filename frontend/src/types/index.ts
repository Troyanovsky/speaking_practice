export interface Turn {
    role: 'user' | 'system';
    text: string;
    audio_url?: string;
}

export interface SessionCreate {
    primary_language: string;
    target_language: string;
    proficiency_level: string;
    stop_word?: string;
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

export interface UserSettings {
    primary_language: string;
    target_language: string;
    proficiency_level: string;
    stop_word: string;
    llm_base_url?: string;
    llm_api_key?: string;
    llm_model?: string;
}
