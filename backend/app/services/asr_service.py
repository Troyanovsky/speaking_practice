import sys
import os

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
                self.model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v3")
        except ImportError:
            print("ASR libraries not installed. Falling back to Mock.")

    async def transcribe(self, audio_path: str) -> str:
        if self.model is None:
            return "This is a mock transcription (ASR libraries missing or model not loaded)."
        
        try:
            IS_MAC = sys.platform == "darwin"

            if IS_MAC:
                result = self.model.transcribe(audio_path)
                return result.text
            else:
                # NeMo for Windows and Linux
                output = self.model.transcribe([audio_path])
                return output[0].text
        except Exception as e:
            print(f"ASR Error: {e}")
            return "Error during transcription."

asr_service = ASRService()
