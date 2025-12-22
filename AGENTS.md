# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project Overview

This is an AI-powered speaking practice application that helps users improve their language skills through interactive voice conversations. The system uses ASR (Parakeet), TTS (Kokoro), and configurable LLM services (any OpenAI-compatible API) to provide real-time conversation practice. Users can select their primary language, target language, and CEFR proficiency level (A1-C2).

## Development Commands

### Backend
```bash
cd backend
uv sync --dev   # Install all dependencies including dev extras
uv run dev      # Development server with auto-reload (http://localhost:8000)
uv run pytest  # Run backend tests with verbose output
make check-comprehensive  # Run all linting and type checking (see LINTING.md)
```

### Frontend
```bash
cd frontend
npm install     # Install dependencies
npm run dev     # Development server (typically http://localhost:5173)
npm run build   # Production build
npm run lint    # ESLint checking
npm test        # Run frontend tests with Vitest
npm run preview # Preview production build
```

## Testing

### Backend
The backend uses pytest for testing with async support:
```bash
cd backend
uv run pytest -v                      # Run all tests with verbose output
uv run pytest tests/unit/             # Run unit tests only
uv run pytest tests/integration/      # Run integration tests only
uv run pytest -k "test_asr_service"   # Run specific test file or pattern
```

### Frontend
The frontend uses Vitest for testing with React Testing Library:
```bash
cd frontend
npm test                               # Run all tests
npm test -- --ui                       # Run tests with Vitest UI
npm test -- --coverage                 # Run tests with coverage report
```

## Code Quality & Linting

The backend uses comprehensive linting tools to maintain code quality:
- **Function length limit**: 50 lines
- **File length limit**: 300 lines
- **Tools**: Black, isort, flake8, mypy, pre-commit hooks

See `backend/LINTING.md` for detailed configuration and usage.

## Architecture Overview

### Backend Structure (FastAPI)
- **Entry Point**: `backend/app/main.py` - FastAPI app with exception handlers, CORS, static file mounting, and background session cleanup
- **API Layer**: `backend/app/api/v1/endpoints/` - HTTP route handlers
  - `session.py` - Session management endpoints
  - `settings.py` - Settings configuration endpoints
  - `history.py` - Session history endpoints
- **Service Layer**: `backend/app/services/` - Business logic and AI integrations
  - `session_manager.py` - Orchestrates session flow, state, and cleanup
  - `llm_service.py` - OpenAI-compatible API integration with dynamic client creation
  - `asr_service.py` - Parakeet speech recognition with platform-specific implementations
  - `tts_service.py` - Kokoro text-to-speech with dynamic language support
  - `history_service.py` - Session history persistence (JSON)
  - `settings_service.py` - User settings persistence (JSON)
- **Core**: `backend/app/core/` - Configuration, exceptions, audio utilities, and conversation topics
  - `config.py` - Application settings and environment variables
  - `exceptions.py` - Custom exception classes (AppException, LLMError, etc.)
  - `audio.py` - Audio processing utilities
  - `topics.py` - Predefined conversation topics organized by CEFR proficiency level
- **Schemas**: `backend/app/schemas/` - Pydantic models for data validation
  - `session.py` - Session-related data models
  - `settings.py` - Settings configuration models
  - `history.py` - History data models
- **Data Storage**: `backend/app/data/` - Runtime data storage
  - `uploads/` - Temporary audio upload directory
  - `outputs/` - Generated TTS audio files (served via `/static`)

### Frontend Structure (React + TypeScript)
- **Main App**: `frontend/src/App.tsx` - Application routing and layout
- **Features**: `frontend/src/features/` - Feature-based modules
  - `practice/` - Core practice session logic and UI with waveform visualization and turn counter
  - `history/` - Conversation history management and display
  - `settings/` - User preferences and configuration
- **Components**: Reusable UI components
  - `AudioRecorder.tsx` - Audio recording functionality
  - `Notification.tsx` - Toast notification display
  - `NotificationContext.tsx` - Notification state management
  - `SessionReview.tsx` - Enhanced session review with conversation history and detailed feedback
- **API Client**: `frontend/src/api/client.ts` - Centralized API calls with error handling
- **Types**: `frontend/src/types/` - TypeScript type definitions
- **Testing**: `frontend/src/test/` - Test setup and utilities

## Key Workflows

### Session Flow
1. Frontend calls `POST /api/v1/session/start` to create session with session ID
2. User records audio and sends via `POST /api/v1/session/{id}/turn`
3. Backend orchestrates: ASR → LLM → TTS → returns response with session-based audio filenames. LLM service now uses predefined topics based on CEFR level for more contextual conversations.
4. Session can end via multiple mechanisms:
   - **Stop Word**: User says stop word during normal turn → generates wrap-up response with `is_session_ending=True`
   - **Max Turns**: Reaches 15 turns → generates natural closing message with `is_session_ending=True`
   - **Stop Button**: User clicks stop button → calls `POST /api/v1/session/{id}/stop` → generates wrap-up response with `is_session_ending=True`
5. Frontend waits for wrap-up audio to complete playing, then calls `POST /api/v1/session/{id}/end` to generate analysis. Session review includes conversation history and detailed feedback with turn-by-turn corrections.
6. Background cleanup task removes expired sessions and associated audio files every 10 minutes

### Audio Handling
- Backend mounts `/static` for serving generated audio files from `data/outputs/`
- Audio files use session-based naming: `{session_id}_{turn_number}.wav`
- Frontend constructs audio URLs: `http://localhost:8000/static/filename`
- Uploaded audio files are temporarily stored in `data/uploads/` with validation

### API Endpoints

#### Session Management
- `POST /api/v1/session/start` - Create new session with language settings
- `POST /api/v1/session/{id}/turn` - Process audio turn with ASR → LLM → TTS pipeline
- `POST /api/v1/session/{id}/stop` - Manually stop session with polite wrap-up response
- `POST /api/v1/session/{id}/end` - Generate final analysis (called after wrap-up completes)

#### Session Ending Behavior
- **Stop Word**: `"The user has decided to stop the session. Please provide a brief, polite wrap-up message in the target language."`
- **Max Turns**: `"This is the final turn of the conversation. Please provide a natural closing message to wrap up the session in the target language."`
- **Stop Button**: Same as stop word prompt

### Error Handling
- Custom exception hierarchy with `AppException` base class
- Structured error responses with error codes, messages, and details
- Frontend notification system for user feedback (success, error, info, warning)
- Global exception handlers in FastAPI for consistent error responses

## Platform-Specific Dependencies

The backend uses platform-specific ASR libraries with automatic fallback:
- **macOS**: `parakeet-mlx` (Apple Silicon optimized)
- **Windows/Linux**: `nemo_toolkit[asr]` with `cuda-python` dependency for non-mac systems
- Both fall back to mock implementations if installation fails
- `hf-transfer>=0.1.9` dependency for improved model downloading

## Environment Configuration

Backend requires `.env` file with LLM configuration (see `.env.example`):
```env
# OpenAI (default)
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_key_here
LLM_MODEL=gpt-4o

# Or use other OpenAI-compatible APIs (Ollama, Azure OpenAI, LocalAI, etc.)
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_API_KEY=ollama
# LLM_MODEL=llama3

# Backward compatibility: OPENAI_API_KEY still works
# OPENAI_API_KEY=your_key_here

# Application settings
PROJECT_NAME=Speaking Practice App
API_V1_STR=/api/v1
```

Frontend can be configured with:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Development Notes

- **Issue Tracking**: `doc/ISSUES.json` - Mark as `passes` only when fully implemented and tested
- **Testing**: pytest (backend) and Vitest (frontend). Add tests for all new features
- **Session Management**: In-memory state, session-based audio cleanup, 1-hour expiration with background cleanup
- **Data Persistence**: JSON-based storage for history (survives restarts) and user settings (persisted as defaults)
- **Security**: Audio upload validation, filename sanitization, structured error handling, CORS (dev: all origins)
- **Architecture**: Clean API/service separation with dependency injection
- **Frontend**: React 19 + TypeScript + Tailwind, optimistic UI updates
- **Key Features**:
  - Session ending UX with `is_session_ending` state and wrap-up flow
  - Enhanced session review with conversation history and turn-by-turn feedback
  - Active session UI with waveform visualization and turn counter
  - Dynamic TTS language support (EN, ES, FR, IT, PT)
  - LLM integration with predefined CEFR topics, enhanced grammar analysis, and markdown stripping