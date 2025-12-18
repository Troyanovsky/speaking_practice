from app.services.asr_service import asr_service
from app.services.tts_service import tts_service

# Verify models are None initially (simulating test environment)
print(f"ASR Model: {asr_service.model}")
print(f"TTS Pipeline: {tts_service.pipeline_object}")

assert asr_service.model is None
assert tts_service.pipeline_object is None

print("Verification Successful: Services initialized without loading models.")
