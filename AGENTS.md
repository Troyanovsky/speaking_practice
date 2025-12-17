# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project Overview

This is an AI-powered speaking practice application that helps users improve their language skills through interactive voice conversations. The system uses ASR (Parakeet), TTS (Kokoro), and LLM (OpenAI GPT) services to provide real-time conversation practice.

## Development Commands

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # Development server (typically http://localhost:5173)
npm run build    # Production build
npm run lint     # ESLint checking
```

## Architecture Overview

### Backend Structure (FastAPI)
- **Entry Point**: `backend/app/main.py` - FastAPI app with CORS and static file mounting
- **API Layer**: `backend/app/api/v1/endpoints/` - HTTP route handlers
- **Service Layer**: `backend/app/services/` - Business logic and AI integrations
  - `session_manager.py` - Orchestrates session flow and state
  - `llm_service.py` - OpenAI API integration
  - `asr_service.py` - Parakeet speech recognition
  - `tts_service.py` - Kokoro text-to-speech
- **Core**: `backend/app/core/` - Configuration and utilities
- **Schemas**: `backend/app/schemas/` - Pydantic models for data validation

### Frontend Structure (React + TypeScript)
- **Main App**: `frontend/src/App.tsx` - Application routing
- **Features**: `frontend/src/features/` - Feature-based modules
  - `practice/` - Core practice session logic
  - `history/` - Conversation history management
  - `settings/` - User preferences
- **Components**: Reusable UI components including `AudioRecorder`
- **API Client**: `frontend/src/api/client.ts` - Centralized API calls

## Key Workflows

### Session Flow
1. Frontend calls `POST /api/v1/session/start` to create session
2. User records audio and sends via `POST /api/v1/session/{id}/turn`
3. Backend orchestrates: ASR → LLM → TTS → returns response
4. Session ends after 15 turns or stop word, analysis generated

### Audio Handling
- Backend mounts `/static` for serving generated audio files
- Audio files are saved to `data/outputs/` directory
- Frontend constructs audio URLs: `http://localhost:8000/static/filename`

## Platform-Specific Dependencies

The backend uses platform-specific ASR libraries:
- **macOS**: `parakeet-mlx`
- **Windows/Linux**: `nemo_toolkit[asr]`
Both fall back to mock implementations if installation fails.

## Environment Configuration

Backend requires `.env` file with:
```env
OPENAI_API_KEY=your_key_here
```

Frontend can be configured with:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Development Notes

- Session state is maintained in-memory (`session_manager.py`) - not persistent across restarts
- Static file serving is handled by FastAPI's `StaticFiles` middleware
- CORS is configured to allow all origins in development
- The architecture follows a clean separation between API layer and business logic
- Frontend uses optimistic UI updates for better user experience