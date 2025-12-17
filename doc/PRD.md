# Speaking Practice App - Product Requirements Document

## 1. Overview
An AI-powered application to help users improve speaking and listening skills through interactive conversation sessions and structured feedback.

## 2. Technical Stack
- **Frontend**: React, Tailwind CSS
- **Backend**: Python (FastAPI/Localhost), managed with `uv`
- **ASR**: Parakeet
- **TTS**: Kokoro TTS
- **LLM**: OpenAI-compatible API

## 3. Core Workflow
### 3.1. Onboarding
- **Inputs**: Primary Language, Target Language, CEFR Level, Stop Word.
- **Persistence**: Settings saved across sessions.

### 3.2. Practice Session
1. **Start**: User initiates session.
2. **Interaction**:
   - LLM greets and requests a topic.
   - If User provides topic -> specific conversation.
   - If User declines -> LLM selects random topic.
3. **Loop**: Max 15 turns (User + System = 1 turn).
4. **Termination**:
   - **Manual**: User speaks "Stop Word" (parsed via ASR).
   - **Automatic**: At 15 turns, LLM wraps up naturally.

### 3.3. Post-Session Review
- **Summary**: High-level recap of the conversation.
- **Detailed Analysis**: Line-by-line grammar and vocabulary feedback (JSON format from LLM).
- **History**: Session log saved for review.

## 4. User Interface
- **Practice Tab**: Main entry point for sessions.
- **History Tab**: List of past conversations.
- **Settings Tab**: Configuration (LLM API, Languages, Proficiency).

## 5. System Prompts
Modularized prompts for distinct tasks:
1. **Conversation**: Persona, turn management.
2. **Summary**: Session recap.
3. **Analysis**: Structured linguistic feedback (JSON).

## Supported Languages
- English, Spanish, French, Italian, Portuguese