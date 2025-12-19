# AI Speaking Practice - Call with Luna

Improve your foreign-language speaking and listening with AI-powered conversations that feel like talking to a real person. Inspired by Duolingo Max's "Call with Lily," this app creates an immersive speaking environment where you can practice your target language anytime, anywhere.

## Features

- **Natural Conversations**: Hold free-flowing voice conversations with an AI tutor that adapts to your skill level and speaking pace
- **Confidence Building**: Practice in a judgment-free zone where mistakes are part of learning—no embarrassment, just progress
- **Real-World Scenarios**: Practice everyday conversations that prepare you for actual interactions with native speakers
- **Instant Feedback**: Get helpful corrections and suggestions without interrupting the flow of conversation
- **Multi-language Support**: Practice English, Spanish, French, Italian, and Portuguese at your own pace
- **Session Reviews**: Access conversation transcripts to review what you learned and track your improvement over time

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

3. Install dependencies and run the server:
   ```bash
   uv sync --dev  # Install dependencies including dev extras for testing
   uv run dev
   ```
   > **Note**: `uv` will automatically create a virtual environment and install dependencies from `pyproject.toml` on the first run. This includes platform-specific ASR libraries (`parakeet-mlx` for Mac, `nemo_toolkit` for Windows). Ensure you have `ffmpeg` installed on your system.

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

#### Testing
Run the backend test suite:
```bash
cd backend
uv run pytest -v  # Run all tests with verbose output
```

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

#### Testing
Run the frontend test suite:
```bash
cd frontend
npm test  # Run Vitest tests
```

## Usage

1. Open the app in your browser and start a conversation
2. Select your primary language, target language, and proficiency level (A1-C2)
3. Click **Start New Session** to begin your conversation
4. Allow microphone access when prompted
5. **Hold Spacebar** to speak naturally—just like talking to a friend! Release when you're done
6. Your AI tutor responds immediately with both audio and text, adapting to your level
7. Sessions last about 15 turns, or say your stop word anytime to end early
8. Review your conversation history to see how much you've improved!

## Troubleshooting

- **Hearing "This is a mock transcription"?** This means the app is using a backup voice recognition system. Check the backend console logs for installation issues.
- **Voice Recognition Not Working?** Make sure your microphone is connected and you've granted browser permissions. Some platforms need additional setup—check the installation guide below.
- **Session Timeouts**: Conversations automatically end after 1 hour to keep the app running smoothly. Just start a new session to continue practicing!
- **Error Messages**: Watch for browser notifications—they'll give you specific details about what's happening.

## Documentation

- [Product Requirements (PRD)](doc/PRD.md)
- [Architecture Guide](doc/ARCHITECTURE.md)
- [Code Review Findings](doc/CODE_REVIEW.md)
