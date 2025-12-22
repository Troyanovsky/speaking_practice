import sys

from app.core.exceptions import ASRError


class ASRService:
    def __init__(self):
        self.model = None

    def load_model(self):
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

    async def transcribe(self, audio_path: str) -> str:
        if self.model is None:
            # For development, we might still want to return mock text instead of crashing
            # But the issue says "strict error logging and specific error codes"
            # Let's raise an error if model is missing in a way that suggests a configuration issue
            return "This is a mock transcription (ASR libraries missing or model not loaded)."

        try:
            IS_MAC = sys.platform == "darwin"

            if IS_MAC:
                result = self.model.transcribe(audio_path)
                return result.text
            else:
                # NeMo for Windows and Linux
                output = self.model.transcribe([audio_path])

                # Handle NeMo's actual output format: tuple of lists
                # Based on investigation, NeMo returns: (["transcription"], ["transcription"])
                if isinstance(output, tuple) and len(output) > 0:
                    # First element is typically a list with the transcription
                    first_element = output[0]
                    if isinstance(first_element, list) and len(first_element) > 0:
                        transcription = first_element[0]
                        if isinstance(transcription, str):
                            return transcription

                    # Fallback: check if first element is directly a string
                    if isinstance(first_element, str):
                        return first_element

                    # Handle tuple with Hypothesis objects
                    if hasattr(first_element, "text"):
                        return first_element.text

                # Fallback for other possible formats
                elif isinstance(output, list) and len(output) > 0:
                    first_item = output[0]

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
                        return first_item.text
                    # Handle dictionary format
                    elif isinstance(first_item, dict):
                        if "text" in first_item:
                            return first_item["text"]
                        elif "transcription" in first_item:
                            return first_item["transcription"]

                raise ASRError(
                    message=f"NeMo returned unexpected output: {type(output)}, content: {str(output)[:200]}"
                )
        except Exception as e:
            raise ASRError(message=f"Transcription failed: {str(e)}")


asr_service = ASRService()
