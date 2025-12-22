"""Audio processing utilities for file validation, conversion, and cleanup."""

import io
import os
import re
from typing import BinaryIO

from fastapi import HTTPException
from pydub import AudioSegment

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".aac", ".flac"}


def sanitize_filename(filename: str | None) -> str:
    """
    Sanitizes a filename to prevent path traversal and other attacks.
    Preserves the extension when truncating to length limit.
    """
    if not filename:
        return "unnamed_audio"

    # Remove directory components (handle both types of separators)
    filename = filename.replace("\\", "/")
    filename = os.path.basename(filename)

    # Remove characters that aren't alphanumeric, dots, underscores, or dashes
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    # Limit length while preserving extension
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[: 255 - len(ext)] + ext

    return filename


def validate_audio_extension(filename: str | None) -> None:
    """
    Validates that the filename has an allowed audio extension.
    """
    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}",
        )


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
        except OSError as fallback_error:
            raise e from fallback_error


def cleanup_session_files(session_id: str) -> None:
    """
    Deletes all uploaded and generated audio files associated with a session.
    """
    from app.core.config import settings

    # Sanitize session_id just in case
    safe_session_id = sanitize_filename(session_id)

    # Check upload directory
    if os.path.exists(settings.AUDIO_UPLOAD_DIR):
        for filename in os.listdir(settings.AUDIO_UPLOAD_DIR):
            if filename.startswith(safe_session_id):
                try:
                    os.remove(os.path.join(settings.AUDIO_UPLOAD_DIR, filename))
                except Exception as e:
                    print(f"Error deleting upload file {filename}: {e}")

    # Check output directory
    if os.path.exists(settings.AUDIO_OUTPUT_DIR):
        for filename in os.listdir(settings.AUDIO_OUTPUT_DIR):
            if filename.startswith(safe_session_id):
                try:
                    os.remove(os.path.join(settings.AUDIO_OUTPUT_DIR, filename))
                except Exception as e:
                    print(f"Error deleting output file {filename}: {e}")
