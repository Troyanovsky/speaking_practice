# Code Review Findings

## Backend (`/backend`)

### 1. In-Memory Session State (`SessionManager`)
- **Issue**: Sessions are stored in a Python dictionary (`self.sessions = {}`).
- **Impact**: All session data is lost if the server restarts (e.g., during deployment or `uvicorn` reload).
- **Recommendation**: Persist sessions to a database (SQLite/PostgreSQL) or Redis. For MVP, file-based persistence (JSON) would suffice.

### 2. Audio File Management
- **Issue**: Uploaded user audio and generated TTS audio accumulate in `data/uploads` and `data/outputs` without cleanup.
- **Impact**: Disk space will eventually fill up.
- **Recommendation**: Implement a cleanup job (e.g., `APScheduler`) to delete files older than X hours, or delete files after the session ends.

### 3. Error Handling in Services
- **Issue**: ASR and TTS services catch broad `Exception` and return mock strings or error paths.
- **Impact**: While good for stability, it masks underlying configuration issues (e.g., missing model weights).
- **Recommendation**: strict error logging and potentially exposing specific error codes to the client so the UI can show "ASR Failed".

### 4. Security
- **Issue**: `CORSMiddleware` allows `allow_origins=["*"]`.
- **Impact**: Security risk in production.
- **Recommendation**: Restrict origins to the specific frontend domain in production configuration.

### 5. `MediaRecorder` Mime Type
- **Issue**: Frontend requests `audio/webm`.
- **Impact**: Safari on iOS/macOS can be picky about `audio/webm`.
- **Recommendation**: Use a polyfill or feature detection to fallback to `audio/mp4` or `audio/wav` if needed, although modern Safari generally supports webm now.

## Frontend (`/frontend`)

### 1. Polling vs Push
- **Observation**: The app sends audio and waits for the full response (ASR + LLM + TTS).
- **Impact**: User waits a long time (Latency = Upload + Transcribe + LLM + Synthesize + Download).
- **Recommendation**: 
    - **Optimistic UI**: Show ASR result as soon as it's done (separate endpoint?) - NO, current design returns all at once.
    - **Streaming**: For lower latency, stream the TTS audio response chunk-by-chunk. This requires backend changes to stream the response.

### 2. Audio Playback
- **Issue**: `new Audio(url).play()` is simple but offers limited control.
- **Impact**: No visualizer, no seek bar, no way to stop playback easily if user interrupts.
- **Recommendation**: Use a more robust audio player component state management.

### 3. Hardcoded Language Settings
- **Issue**: `PracticeView` has hardcoded "English" -> "Spanish".
- **Impact**: Users cannot actually change settings despite the endpoint supporting it.
- **Recommendation**: Connect the `SessionCreate` payload to a UI selector/Settings form (as planned in PRD but not yet implemented in UI).

## Conclusion
The current implementation is a solid **MVP/Proof of Concept**. It meets the functional requirements for a single-user local demo. To move to production or a robust beta, persistence and cleanup are the highest priority backend tasks, while error handling and latency optimization (streaming) are key for UX.
