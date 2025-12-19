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
│   │   │   ├── exceptions.py # Custom exception classes
│   │   │   └── audio.py      # Audio processing utilities
│   │   ├── services/         # Business Logic & AI Integrations
│   │   │   ├── llm_service.py     # OpenAI-compatible API wrapper with dynamic client creation
│   │   │   ├── asr_service.py     # Parakeet ASR wrapper with platform-specific implementations
│   │   │   ├── tts_service.py     # Kokoro TTS wrapper with dynamic language support
│   │   │   ├── session_manager.py # Manages session state, turn counting & cleanup
│   │   │   ├── history_service.py # Persists completed sessions to JSON
│   │   │   └── settings_service.py # User settings persistence
│   │   └── schemas/          # Pydantic Models (Data validation)
│   │       ├── session.py
│   │       ├── history.py
│   │       ├── chat.py
│   │       └── settings.py
│   ├── data/                 # Local persistence (JSON/SQLite)
│   │   ├── uploads/          # Temporary audio upload directory
│   │   └── outputs/          # Generated TTS audio files
│   ├── tests/                # Backend tests
│   │   ├── unit/             # Unit tests
│   │   └── integration/      # Integration tests
│   ├── pyproject.toml
│   └── uv.lock
│
├── frontend/                 # React/Tailwind Frontend
│   ├── src/
│   │   ├── components/       # Reusable UI Components
│   │   │   ├── AudioRecorder.tsx    # Audio recording functionality
│   │   │   ├── Notification.tsx     # Toast notification display
│   │   │   └── NotificationContext.tsx # Notification state management
│   │   ├── features/         # Feature-based modules
│   │   │   ├── practice/     # Practice Session Logic
│   │   │   │   ├── PracticeView.tsx
│   │   │   │   └── SessionReview.tsx
│   │   │   ├── history/      # History Logic
│   │   │   │   ├── HistoryView.tsx
│   │   │   │   └── HistoryDetail.tsx
│   │   │   └── settings/     # Settings Logic
│   │   │       └── SettingsView.tsx
│   │   ├── api/              # API Client (axios/fetch wrappers)
│   │   ├── types/            # TypeScript Interfaces
│   │   ├── test/             # Test setup and utilities
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
    *   **Responsibility**: Business logic handling.
        *   `llm_service`: Handles all prompt construction and LLM API calls. Supports any OpenAI-compatible API with dynamic client creation, configurable base URL, API key, and model. Generates context-aware responses based on user's proficiency level and language settings.
        *   `asr_service`: Receives audio files with validation, runs Parakeet (platform-specific), returns text. Includes filename sanitization and security checks.
        *   `tts_service`: Receives text, runs Kokoro with dynamic language support (English, Spanish, French, Italian, Portuguese), returns audio bytes with session-based naming.
        *   `session_manager`: Orchestrates the flow and manages session lifecycle. When `session.py` router receives audio input, the manager calls `asr_service` -> adds to history -> calls `llm_service` -> calls `tts_service` -> updates state. Includes background cleanup task for expired sessions.
    *   **Connection**: DEPENDS ON `app.core` (config, exceptions), `app.schemas`.
*   **`app.core`**:
    *   Holds singleton configurations and keys.

### 2.2 Frontend Modules

*   **`features/practice`**:
    *   **Responsibility**: Handles the live session.
    *   **Logic**: Manages session state (recording, turn data). Includes language selection UI allowing users to choose primary language, target language, and CEFR proficiency level. Provides session review with analysis after completion.
    *   **Connection**: Calls `api/client` to interact with backend endpoints.
*   **`features/history`**:
    *   **Responsibility**: Manages conversation history display and navigation.
    *   **Logic**: Fetches and displays past sessions with detailed analysis and feedback.
*   **`features/settings`**:
    *   **Responsibility**: User preferences and LLM configuration management.
    *   **Logic**: Forms for setting API keys, model selection, and language preferences.
*   **`components`**:
    *   **Responsibility**: Reusable UI components with notification system.
    *   **Logic**: `AudioRecorder` for voice recording, `Notification` system for user feedback, `NotificationContext` for global state management.
*   **`api`**:
    *   **Responsibility**: Centralized place for all API calls with error handling. Ensures types match `backend/app/schemas` and provides structured error feedback.

## 3. Data Flow

### Scenario: User Speaks a Sentence

1.  **Frontend (`PracticeView`)**: User selects primary language, target language, and CEFR level, then records audio. Long-press spacebar to record, release to end recording and send.
2.  **Frontend (`api`)**: `POST /api/v1/session/{id}/turn` with validated audio file.
3.  **Backend (`api/endpoints/session.py`)**: Receives file with validation and error handling.
4.  **Backend (`session_manager`)**:
    *   Validates audio file (filename sanitization, extension check).
    *   Calls `asr_service.transcribe(audio_file)` with platform-specific implementation.
    *   Checks for "Stop Word".
    *   If continue:
        *   Appends user text to conversation history.
        *   Calls `llm_service.get_response(history, user_language_settings)` with dynamic client creation.
        *   LLM generates context-aware response based on proficiency level and language settings.
        *   Calls `tts_service.synthesize(llm_response_text)` with session-based naming and language support.
        *   Updates session state (turn count + 1).
5.  **Backend (`api`)**: Returns structured JSON `{ "user_text": "...", "ai_text": "...", "ai_audio_url": "..." }` with error handling.
6.  **Frontend**: Plays audio, displays text updates, handles any notifications.

### Scenario: End of Session Analysis

1.  **Backend**: When turn count == 15 or stop word detected.
2.  **Backend (`session_manager`)**:
    *   Calls `llm_service.generate_summary(history)` with dynamic client.
    *   Calls `llm_service.analyze_grammar(history)` (Returns JSON).
    *   Saves full record to `data/history.json` with absolute path resolution.
    *   Marks session for cleanup after 1 hour.
3.  **Frontend**: Redirects to History Detail view to show the report with session review.

### Scenario: Session Cleanup

1.  **Background Task**: Runs every 10 minutes in `main.py`.
2.  **Backend (`session_manager`)**:
    *   Identifies sessions older than 1 hour (3600 seconds).
    *   Removes session state from memory.
    *   Deletes associated audio files from `data/outputs/` using session-based naming.
    *   Logs cleanup activity.

### Scenario: Error Handling

1.  **Backend**: Any service raises `AppException` with error code and details.
2.  **Global Exception Handler** in `main.py` catches and formats structured error responses.
3.  **Frontend**: `NotificationContext` receives error, displays user-friendly toast notifications.

## Relevant Docs
Kokoro TTS docs: doc/kokoro_tts_doc.md
Parakeet ASR docs: doc/parakeet_doc.md
