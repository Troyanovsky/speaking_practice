# AI Speaking Practice App

An AI-powered application to help users improve speaking and listening skills through interactive conversation sessions. The app uses advanced AI models for Speech-to-Text (ASR), Text-to-Speech (TTS), and conversation logic (LLM).

## Features

- **Interactive Conversation**: Real-time voice interaction with an AI tutor.
- **Multi-language Support**: Designed to support English, Spanish, French, Italian, and Portuguese.
- **Feedback & Analysis**: Provides grammar and vocabulary feedback after each session.
- **Conversation History**: Access past sessions to review progress and previous feedback.
- **Local AI Inference**: Optimized for local execution using Parakeet (ASR) and Kokoro (TTS).

## Tech Stack

- **Frontend**: React, TypeScript, Tailwind CSS, Vite.
- **Backend**: FastAPI, Python.
- **AI Services**:
    - **ASR**: Parakeet (via `parakeet-mlx` on Mac, `nemo_toolkit` on Windows).
    - **TTS**: Kokoro (via `kokoro` library).
    - **LLM**: Any OpenAI-compatible API (OpenAI GPT-4o, Azure OpenAI, Ollama, LocalAI, etc.).

## Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- An LLM provider API key (OpenAI, Azure OpenAI, or compatible API)

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Configure Environment:
   Create a `.env` file in `backend/` and add your LLM configuration (see [below](#configure-environment) for options).

3. Run the server:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   > **Note**: `uv` will automatically create a virtual environment and install dependencies from `requirements.txt` on the first run. This includes platform-specific ASR libraries (`parakeet-mlx` for Mac, `nemo_toolkit` for Windows). Ensure you have `ffmpeg` installed on your system.

#### Configure Environment
Create a `.env` file in `backend/` with your settings:
```env
# Option 1: OpenAI (default)
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-openai-api-key-here
LLM_MODEL=gpt-4o

# Option 2: Local LLM via Ollama
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_API_KEY=ollama
# LLM_MODEL=llama3

# Option 3: Azure OpenAI
# LLM_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
# LLM_API_KEY=your-azure-api-key
# LLM_MODEL=gpt-4
```

The API will be available at `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.

### Security Note

> [!CAUTION]
> This application stores sensitive information, including API keys, in a local JSON file (`backend/app/data/user_settings.json`). This file is not encrypted. This storage method is intended for **local single-user use only**. Do not deploy this application to a public server without implementing a secure storage solution for credentials.

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
2. Select your primary language, target language, and proficiency level (A1-C2).
3. Click **Start New Session**.
4. Allow microphone access when prompted.
5. **Hold Spacebar** to speak. Release to send your audio.
6. The AI will reply with audio and text, tailored to your proficiency level.
7. The session ends automatically after 15 turns or if you say "Stop".

## Troubleshooting

- **ASR/TTS Errors**: If you see "This is a mock transcription" or hear mock audio, it means the backend handling failed to load the real libraries (likely due to missing dependencies or unsupported platform) and fell back to the mock implementation. Check the backend console logs.
- **Dependencies**: `nemo_toolkit` can be tricky to install on some Windows setups. Refer to NVIDIA NeMo documentation.

## Documentation

- [Product Requirements (PRD)](doc/PRD.md)
- [Architecture Guide](doc/ARCHITECTURE.md)
- [Code Review Findings](doc/CODE_REVIEW.md)
