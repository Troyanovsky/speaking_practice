import os
import uuid
import soundfile as sf
from app.core.config import settings

pipeline_object = None

try:
    from kokoro import KPipeline
    # Initialize pipeline for US English ('a') by default
    # Ideally, this should be dynamic based on language, but for MVP sticking to 'a'
    print("Loading Kokoro Pipeline...")
    pipeline_object = KPipeline(lang_code='a') 
except ImportError:
    print("Kokoro library not installed. Falling back to Mock.")

class TTSService:
    async def synthesize(self, text: str) -> str:
        if pipeline_object is None:
            return "/static/mock_audio.wav"

        try:
            # Generate unique filename
            filename = f"{uuid.uuid4()}.wav"
            output_path = os.path.join(settings.AUDIO_OUTPUT_DIR, filename)
            
            # Generate audio
            # voice='af_heart' is a good default
            generator = pipeline_object(text, voice='af_heart', speed=1, split_pattern=r'\n+')
            
            # Concatenate audio chunks (simplification: assume single chunk or taking first useful)
            # A real impl might need to stitch if text is long
            has_audio = False
            for i, (gs, ps, audio) in enumerate(generator):
                # Save just the first chunk for MVP or stitch them
                # For this demo let's save the first chunk
                sf.write(output_path, audio, 24000)
                has_audio = True
                break 
            
            if has_audio:
                return f"/static/{filename}"
            else:
                return "/static/error.wav"

        except Exception as e:
            print(f"TTS Error: {e}")
            return "/static/error_tts.wav"

tts_service = TTSService()
