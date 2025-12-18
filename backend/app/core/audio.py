import os
import io
from typing import BinaryIO
from pydub import AudioSegment

def save_upload_file(upload_file: BinaryIO, destination: str) -> str:
    """
    Saves and processes an uploaded audio file.
    Converts to WAV, 16kHz, Mono for optimal ASR.
    """
    try:
        # Read the uploaded file content
        content = upload_file.read()
        audio_stream = io.BytesIO(content)
        
        # Load audio from stream
        # Try to detect format or let pydub handle it
        audio = AudioSegment.from_file(audio_stream)
        
        # Standardize: 16kHz, Mono, 16-bit
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        
        # Ensure destination is .wav
        base_dest, _ = os.path.splitext(destination)
        final_dest = f"{base_dest}.wav"
        
        # Export as wav
        audio.export(final_dest, format="wav")
        return final_dest
    except Exception as e:
        print(f"Error processing audio file: {e}")
        # Fallback to simple save if processing fails (might be useful for debugging)
        try:
            upload_file.seek(0)
            with open(destination, "wb") as buffer:
                buffer.write(upload_file.read())
            return destination
        except:
            raise e
