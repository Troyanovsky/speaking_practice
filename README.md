# AI Speaking Practice App

An AI-powered application to help users improve speaking and listening skills through interactive conversation sessions. The app uses advanced AI models for Speech-to-Text (ASR), Text-to-Speech (TTS), and conversation logic (LLM).

## Features

- **Interactive Conversation**: Real-time voice interaction with an AI tutor.
- **Multi-language Support**: Designed to support English, Spanish, French, Italian, and Portuguese.
- **Feedback & Analysis**: Provides grammar and vocabulary feedback after each session.
- **Local AI Inference**: Optimized for local execution using Parakeet (ASR) and Kokoro (TTS).

## Tech Stack

- **Frontend**: React, TypeScript, Tailwind CSS, Vite.
- **Backend**: FastAPI, Python.
- **AI Services**:
    - **ASR**: Parakeet (via `parakeet-mlx` on Mac, `nemo_toolkit` on Windows).
    - **TTS**: Kokoro (via `kokoro` library).
    - **LLM**: OpenAI GPT-4o (or compatible API).

## Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- An OpenAI API Key

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > **Note**: This will install platform-specific ASR libraries (`parakeet-mlx` for Mac, `nemo_toolkit` for Windows). Ensure you have the necessary system dependencies (e.g., ffmpeg).

4. Configure Environment:
   Create a `.env` file in `backend/` and add your OpenAI Key:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The app will typically run at `http://localhost:5173`.

## Usage

1. Open the frontend URL in your browser.
2. Click **Start New Session**.
3. Allow microphone access when prompted.
4. **Hold Spacebar** to speak. Release to send your audio.
5. The AI will reply with audio and text.
6. The session ends automatically after 15 turns or if you say "Stop".

## Troubleshooting

- **ASR/TTS Errors**: If you see "This is a mock transcription" or hear mock audio, it means the backend handling failed to load the real libraries (likely due to missing dependencies or unsupported platform) and fell back to the mock implementation. Check the backend console logs.
- **Dependencies**: `nemo_toolkit` can be tricky to install on some Windows setups. Refer to NVIDIA NeMo documentation.

## Documentation

- [Product Requirements (PRD)](doc/PRD.md)
- [Architecture Guide](doc/ARCHITECTURE.md)
- [Code Review Findings](doc/CODE_REVIEW.md)
