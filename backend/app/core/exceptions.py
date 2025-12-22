"""Custom exception classes for the application."""

from typing import Any, Optional

from fastapi import status


class AppException(Exception):
    """Base exception class for application errors."""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.detail = detail
        super().__init__(message)


class SessionError(AppException):
    """Exception raised for session-related errors."""

    def __init__(
        self, message: str = "Session error occurred", detail: Optional[Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="SESSION_ERROR",
            message=message,
            detail=detail,
        )


class SessionNotFoundError(AppException):
    """Exception raised when a session is not found."""

    def __init__(self, session_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="SESSION_NOT_FOUND",
            message=f"Session {session_id} not found",
            detail={"session_id": session_id},
        )


class ASRError(AppException):
    """Exception raised for automatic speech recognition errors."""

    def __init__(
        self, message: str = "Speech recognition failed", detail: Optional[Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="ASR_ERROR",
            message=message,
            detail=detail,
        )


class TTSError(AppException):
    """Exception raised for text-to-speech synthesis errors."""

    def __init__(
        self, message: str = "Speech synthesis failed", detail: Optional[Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="TTS_ERROR",
            message=message,
            detail=detail,
        )


class LLMError(AppException):
    """Exception raised for language model processing errors."""

    def __init__(
        self, message: str = "Language model error", detail: Optional[Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="LLM_ERROR",
            message=message,
            detail=detail,
        )


class ValidationError(AppException):
    """Exception raised for data validation errors."""

    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
            detail=detail,
        )
