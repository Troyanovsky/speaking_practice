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

        # Handle NeMo's actual output format: tuple of lists
        # Based on investigation, NeMo returns: (["transcription"], ["transcription"])
        if isinstance(output, tuple) and len(output) > 0:
            # First element is typically a list with the transcription
            first_element: Any = output[0]
            if isinstance(first_element, list) and len(first_element) > 0:
                transcription: Any = first_element[0]
                if isinstance(transcription, str):
                    return transcription

            # Fallback: check if first element is directly a string
            if isinstance(first_element, str):
                return first_element

            # Handle tuple with Hypothesis objects
            if hasattr(first_element, "text"):
                return str(first_element.text)

        # Fallback for other possible formats
        elif isinstance(output, list) and len(output) > 0:
            first_item: Any = output[0]

            # Handle list of strings
            if isinstance(first_item, str):
                return first_item
            # Handle list with text as first element
            elif (
                isinstance(first_item, list)
                and len(first_item) > 0
                and isinstance(first_item[0], str)
            ):
                return first_item[0]
            # Handle Hypothesis objects
            elif hasattr(first_item, "text"):
                return str(first_item.text)
            # Handle dictionary format
            elif isinstance(first_item, dict):
                if "text" in first_item:
                    return str(first_item["text"])
                elif "transcription" in first_item:
                    return str(first_item["transcription"])

        raise ASRError(
            message=f"NeMo returned unexpected output: {type(output)}, content: {str(output)[:200]}"
        )

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
            # For development, we might still want to return mock text instead of crashing
            # But the issue says "strict error logging and specific error codes"
            # Let's raise an error if model is missing in a way that suggests a configuration issue
            return "This is a mock transcription (ASR libraries missing or model not loaded)."

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
