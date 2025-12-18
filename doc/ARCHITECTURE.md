# System Architecture & Implementation Guide

## 1. Modular Folder Structure

The project is divided into two main, independent directories: `backend` and `frontend`. This allows for clear separation of concerns and independent development cycles.

```text
speaking_practice/
├── backend/                  # Python/FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # Entry point, app initialization
│   │   ├── api/              # API Route Handlers
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── session.py   # Practice session endpoints (start, turn, end)
│   │   │   │   │   ├── history.py   # Past conversation history
│   │   │   │   │   └── settings.py  # User settings management
│   │   │   │   └── api.py       # Route aggregation
│   │   ├── core/             # Core infrastructure
│   │   │   ├── config.py     # Environment vars & configuration
│   │   │   └── audio.py      # Audio processing utilities
│   │   ├── services/         # Business Logic & AI Integrations
│   │   │   ├── llm_service.py     # OpenAI API wrapper (Conversation, Summary, Analysis)
│   │   │   ├── asr_service.py     # Parakeet ASR wrapper
│   │   │   ├── tts_service.py     # Kokoro TTS wrapper
│   │   │   ├── session_manager.py # Manages session state & turn counting
│   │   │   ├── history_service.py # Persists completed sessions to JSON
│   │   │   └── settings_service.py # User settings persistence
│   │   └── schemas/          # Pydantic Models (Data validation)
│   │       ├── session.py
│   │       ├── history.py
│   │       ├── chat.py
│   │       └── settings.py
│   ├── data/                 # Local persistence (JSON/SQLite)
│   ├── tests/                # Backend tests
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/                 # React/Tailwind Frontend
│   ├── src/
│   │   ├── components/       # Reusable UI Components (Button, Card, AudioRecorder)
│   │   ├── features/         # Feature-based modules
│   │   │   ├── practice/     # Practice Session Logic
│   │   │   │   ├── PracticeView.tsx
│   │   │   │   └── usePracticeSession.ts
│   │   │   ├── history/      # History Logic
│   │   │   │   ├── HistoryList.tsx
│   │   │   │   └── HistoryDetail.tsx
│   │   │   └── settings/     # Settings Logic
│   │   │       └── SettingsForm.tsx
│   │   ├── api/              # API Client (axios/fetch wrappers)
│   │   ├── types/            # TypeScript Interfaces
│   │   ├── App.tsx           # Main Routing
│   │   └── index.css         # Tailwind directives
│   ├── package.json
│   └── ...
└── doc/
    ├── PRD.md
    └── ARCHITECTURE.md
```

## 2. Module Responsibilities & Connections

### 2.1 Backend Modules

*   **`app.api` (Router Layer)**:
    *   **Responsibility**: Receives HTTP requests, validates input using `app.schemas`, and calls the appropriate service in `app.services`.
    *   **Connection**: DEPENDS ON `app.schemas`, `app.services`.
*   **`app.services` (Service Layer)**:
    *   **Responsibility**: proper logic handling.
        *   `llm_service`: Handles all prompt construction and LLM API calls. Supports any OpenAI-compatible API with configurable base URL, API key, and model. Generates context-aware responses based on user's proficiency level and language settings.
        *   `asr_service`: Receives audio bytes, runs Parakeet, returns text.
        *   `tts_service`: Receives text, runs Kokoro, returns audio bytes.
        *   `session_manager`: Orchestrates the flow. When `session.py` router receives an audio input, the manager calls `asr_service` -> adds to history -> calls `llm_service` -> calls `tts_service` -> updates state.
    *   **Connection**: DEPENDS ON `app.core` (config), `app.schemas`.
*   **`app.core`**:
    *   Holds singleton configurations and keys.

### 2.2 Frontend Modules

*   **`features/practice`**:
    *   **Responsibility**: Handles the live session.
    *   **Logic**: Uses `usePracticeSession` hook to manage state (recording, specific turn data). Includes language selection UI allowing users to choose primary language, target language, and CEFR proficiency level before starting a session.
    *   **Connection**: Calls `api/client` to interact with backend endpoints.
*   **`api`**:
    *   **Responsibility**: Centralized place for all fetch calls. Ensures types match `backend/app/schemas`.

## 3. Data Flow

### Scenario: User Speaks a Sentence

1.  **Frontend (`PracticeView`)**: User selects primary language, target language, and CEFR level, then records audio. Long-press spacebar to record, release to end recording and send.
2.  **Frontend (`api`)**: `POST /api/v1/session/{id}/turn` with audio file.
3.  **Backend (`api/endpoints/session.py`)**: Receives file.
4.  **Backend (`session_manager`)**:
    *   Calls `asr_service.transcribe(audio_file)`.
    *   Checks for "Stop Word".
    *   If continue:
        *   Appends user text to conversation history.
        *   Calls `llm_service.get_response(history, user_language_settings)`.
        *   LLM generates context-aware response based on proficiency level and language settings.
        *   Calls `tts_service.synthesize(llm_response_text)`.
        *   Updates session state (turn count + 1).
5.  **Backend (`api`)**: Returns JSON `{ "user_text": "...", "ai_text": "...", "ai_audio_url": "..." }`.
6.  **Frontend**: Plays audio, displays text updates.

### Scenario: End of Session Analysis

1.  **Backend**: When turn count == 15 or stop word detected.
2.  **Backend (`session_manager`)**:
    *   Calls `llm_service.generate_summary(history)`.
    *   Calls `llm_service.analyze_grammar(history)` (Returns JSON).
    *   Saves full record to `data/history.json` (or DB).
3.  **Frontend**: Redirects to History Detail view to show the report.

## Relevant Docs
Kokoro TTS docs: doc/kokoro_tts_doc.md
Parakeet ASR docs: doc/parakeet_doc.md
