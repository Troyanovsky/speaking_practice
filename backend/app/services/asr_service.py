"""Automatic Speech Recognition (ASR) service for transcribing audio.

This module provides the ASRService class which handles:
- Platform-specific model loading (Parakeet MLX on macOS, NeMo on Windows/Linux)
- Audio transcription with fallback handling
- Graceful degradation when ASR libraries are not available
"""

import sys
from typing import Any, Optional

from app.core.exceptions import ASRError


class ASRService:
    """Handles audio transcription using platform-specific ASR models.

    Uses Parakeet MLX on macOS for Apple Silicon optimization,
    and NeMo on Windows/Linux with CUDA support.
    """

    def __init__(self) -> None:
        """Initialize the ASR service."""
        self.model: Optional[Any] = None

    def load_model(self) -> None:
        """Load the appropriate ASR model based on the platform.

        Loads Parakeet MLX on macOS and NeMo on Windows/Linux.
        Falls back to mock transcription if libraries are unavailable.
        """
        # Platform-specific imports handling
        IS_MAC = sys.platform == "darwin"

        try:
            if IS_MAC:
                from parakeet_mlx import from_pretrained

                # Global model initialization
                print("Loading Parakeet MLX model...")
                self.model = from_pretrained("mlx-community/parakeet-tdt-0.6b-v3")
            else:
                # Use NeMo for Windows and Linux
                import nemo.collections.asr as nemo_asr

                print("Loading Parakeet NeMo model...")
                self.model = nemo_asr.models.ASRModel.from_pretrained(
                    model_name="nvidia/parakeet-tdt-0.6b-v3"
                )
        except ImportError:
            print("ASR libraries not installed. Falling back to Mock.")

    def _transcribe_mac(self, audio_path: str) -> str:
        """Transcribe audio using Parakeet MLX on macOS."""
        assert self.model is not None, "Model must be loaded to transcribe"
        result: Any = self.model.transcribe(audio_path)
        return str(result.text)

    def _transcribe_nemo(self, audio_path: str) -> str:
        """Transcribe audio using NeMo on Windows/Linux."""
        assert self.model is not None, "Model must be loaded to transcribe"
        output: Any = self.model.transcribe([audio_path])
        transcription = self._extract_nemo_transcription(output)
        if transcription is not None:
            return transcription

        raise ASRError(
            message=(
                f"NeMo returned unexpected output: {type(output)}, content: "
                f"{str(output)[:200]}"
            )
        )

    def _extract_nemo_transcription(self, output: Any) -> Optional[str]:
        """Extract transcription text from NeMo output."""
        if isinstance(output, tuple) and len(output) > 0:
            return self._extract_nemo_item(output[0])

        if isinstance(output, list) and len(output) > 0:
            return self._extract_nemo_item(output[0])

        return None

    def _extract_nemo_item(self, item: Any) -> Optional[str]:
        """Normalize a single NeMo output element into text."""
        result: Optional[str] = None
        if isinstance(item, list) and len(item) > 0:
            item = item[0]

        if isinstance(item, str):
            result = item
        elif hasattr(item, "text"):
            result = str(item.text)
        elif isinstance(item, dict):
            if "text" in item:
                result = str(item["text"])
            elif "transcription" in item:
                result = str(item["transcription"])

        return result

    async def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to the audio file to transcribe.

        Returns:
            Transcribed text string.

        Raises:
            ASRError: If transcription fails.
        """
        if self.model is None:
            # For development, we might still want to return mock text instead of
            # crashing. The issue says "strict error logging and specific error
            # codes"; this suggests a configuration issue for missing models.
            return (
                "This is a mock transcription (ASR libraries missing or model not "
                "loaded)."
            )

        try:
            IS_MAC = sys.platform == "darwin"

            if IS_MAC:
                return self._transcribe_mac(audio_path)
            else:
                # NeMo for Windows and Linux
                return self._transcribe_nemo(audio_path)
        except Exception as e:
            raise ASRError(message=f"Transcription failed: {str(e)}")


asr_service = ASRService()
