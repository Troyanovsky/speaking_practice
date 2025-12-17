import sys
import os

# Platform-specific imports handling
IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"

model = None

try:
    if IS_MAC:
        from parakeet_mlx import from_pretrained
        # Global model initialization
        print("Loading Parakeet MLX model...")
        model = from_pretrained("mlx-community/parakeet-tdt-0.6b-v3")
    elif IS_WIN:
        import nemo.collections.asr as nemo_asr
        print("Loading Parakeet NeMo model...")
        model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v3")
    else:
        print("Warning: Unsupported platform for Parakeet ASR. Using mock.")
except ImportError:
    print("ASR libraries not installed. Falling back to Mock.")

class ASRService:
    async def transcribe(self, audio_path: str) -> str:
        if model is None:
            return "This is a mock transcription (ASR libraries missing)."
        
        try:
            if IS_MAC:
                result = model.transcribe(audio_path)
                return result.text
            elif IS_WIN:
                output = model.transcribe([audio_path])
                return output[0].text
            else:
                return "Unsupported platform."
        except Exception as e:
            print(f"ASR Error: {e}")
            return "Error during transcription."

asr_service = ASRService()
