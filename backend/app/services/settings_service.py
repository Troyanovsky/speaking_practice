import json
import os
from typing import Any, Dict, Optional

from app.core.config import settings as app_settings
from app.schemas.settings import UserSettings


class SettingsService:
    def __init__(self) -> None:
        self.settings_file = os.path.join(
            app_settings.AUDIO_UPLOAD_DIR, "..", "user_settings.json"
        )
        self.settings_file = os.path.abspath(self.settings_file)
        self._settings: Optional[UserSettings] = None

    def _load_settings(self) -> UserSettings:
        if not os.path.exists(self.settings_file):
            return UserSettings(
                llm_base_url=app_settings.LLM_BASE_URL,
                llm_api_key=app_settings.LLM_API_KEY,
                llm_model=app_settings.LLM_MODEL,
            )

        try:
            with open(self.settings_file, "r") as f:
                data = json.load(f)
            return UserSettings(**data)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return UserSettings(
                llm_base_url=app_settings.LLM_BASE_URL,
                llm_api_key=app_settings.LLM_API_KEY,
                llm_model=app_settings.LLM_MODEL,
            )

    def get_settings(self) -> UserSettings:
        if self._settings is None:
            self._settings = self._load_settings()
        return self._settings

    def update_settings(self, new_settings: Dict[str, Any]) -> UserSettings:
        current_settings = self.get_settings()
        # Merge new settings with existing ones
        updated_data = current_settings.model_dump()
        updated_data.update(new_settings)

        self._settings = UserSettings(**updated_data)
        self._save_settings()
        return self._settings

    def _save_settings(self) -> None:
        if self._settings:
            try:
                with open(self.settings_file, "w") as f:
                    json.dump(self._settings.model_dump(), f, indent=4)
            except Exception as e:
                print(f"Error saving settings: {e}")


settings_service = SettingsService()
