"""Large Language Model (LLM) service for AI conversations.

This module provides the LLMService class which handles:
- Dynamic OpenAI-compatible API client creation
- Context-aware conversation responses based on proficiency level
- Grammar analysis with bilingual feedback
- Markdown text cleaning for audio synthesis
- Integration with predefined CEFR topics
"""

import json
import re
from typing import Dict, List, Tuple

from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from app.core.exceptions import LLMError
from app.core.topics import get_topic_for_level
from app.schemas.session import SessionAnalysis
from app.services.settings_service import settings_service


class LLMService:
    """Handles LLM interactions for conversation practice.

    Supports any OpenAI-compatible API with dynamic client creation
    based on user settings.
    """

    def __init__(self) -> None:
        """Initialize the LLM service."""
        # Client is now created dynamically per request to support setting changes
        pass

    def _get_client(self) -> Tuple[AsyncOpenAI, str]:
        """Create a dynamic OpenAI client based on current settings.

        Returns:
            Tuple of (OpenAI client, model name).
        """
        user_settings = settings_service.get_settings()
        client = AsyncOpenAI(
            api_key=user_settings.llm_api_key, base_url=user_settings.llm_base_url
        )
        return client, user_settings.llm_model or "gpt-4o"

    def _clean_text(self, text: str) -> str:
        """Remove markdown formatting and normalize whitespace for TTS.

        Args:
            text: Text potentially containing markdown formatting.

        Returns:
            Cleaned text with markdown removed and whitespace normalized.
        """
        # Remove code blocks and inline code (do this first)
        text = re.sub(r"`{1,3}.*?`{1,3}", "", text, flags=re.DOTALL)
        # Remove bold/italic markers
        text = re.sub(r"[*_]{1,3}", "", text)
        # Remove markdown links [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # Remove list markers at start of lines or after whitespace
        text = re.sub(r"(?m)^\s*[-+*]\s+", "", text)
        text = re.sub(r"(?m)^\s*\d+\.\s+", "", text)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    async def generate_greeting(
        self,
        target_language: str,
        proficiency_level: str,
        primary_language: str = "English",
    ) -> str:
        """Generate a contextual greeting for starting a practice session.

        Args:
            target_language: Language the user is learning.
            proficiency_level: CEFR proficiency level (A1-C2).
            primary_language: User's native language (default: English).

        Returns:
            Greeting text in the target language with topic suggestion.

        Raises:
            LLMError: If greeting generation fails.
        """
        client, model = self._get_client()

        # Get a predefined topic for the proficiency level
        topic = get_topic_for_level(proficiency_level)

        system_prompt = (
            "You are a helpful language learning assistant for "
            f"{target_language} at {proficiency_level} level. Your name is Luna.\n\n"
            "Generate a friendly greeting that:\n"
            "1. Welcomes the user warmly\n"
            f'2. Suggests the following conversation topic: "{topic}"\n'
            "3. Asks an opening question to start the practice\n\n"
            "Keep your response appropriate for a "
            f"{proficiency_level} learner. "
            "Keep the greeting short and to the point.\n\n"
            "CRITICAL: You MUST respond EXCLUSIVELY in "
            f"{target_language}. All parts of your response (greeting, topic "
            "suggestion, and question) must be in "
            f"{target_language}. Keep the greeting concise (2-3 sentences).\n\n"
            "DO NOT use any markdown formatting such as bold (**text**), italics "
            "(*text*), or lists. Return only pure text sentences."
        )

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    ChatCompletionSystemMessageParam(
                        role="system", content=system_prompt
                    ),
                    ChatCompletionUserMessageParam(
                        role="user",
                        content=(
                            "Generate a greeting to start the practice session in "
                            f"{target_language} about the topic: {topic}"
                        ),
                    ),
                ],
            )
            content = response.choices[0].message.content
            return self._clean_text(content or "")
        except Exception as e:
            raise LLMError(message=f"Greeting generation failed: {str(e)}")

    async def get_response(
        self,
        history: List[Dict[str, str]],
        target_language: str = "English",
        proficiency_level: str = "B1",
    ) -> str:
        """Generate an AI response based on conversation history.

        Args:
            history: List of previous conversation turns.
            target_language: Language the user is learning.
            proficiency_level: CEFR proficiency level (A1-C2).

        Returns:
            AI response text in the target language.

        Raises:
            LLMError: If response generation fails.
        """
        client, model = self._get_client()

        system_prompt = (
            "You are a helpful language learning assistant named Luna, helping a "
            f"user practice {target_language} at {proficiency_level} level.\n\n"
            "Adjust your language complexity to match their proficiency.\n\n"
            "Keep your responses concise (2-3 sentences max) and natural (as if "
            "talking to a friend). Encourage the user to speak more.\n"
            "CRITICAL: You MUST respond EXCLUSIVELY in "
            f"{target_language}. Do not use any other language.\n\n"
            "DO NOT use any markdown formatting such as bold (**text**), italics "
            "(*text*), or lists. Return only pure text sentences."
        )

        messages: List[
            ChatCompletionSystemMessageParam
            | ChatCompletionUserMessageParam
            | ChatCompletionAssistantMessageParam
        ] = [ChatCompletionSystemMessageParam(role="system", content=system_prompt)]
        messages.extend(
            [
                (
                    ChatCompletionUserMessageParam(role="user", content=msg["content"])
                    if msg["role"] == "user"
                    else ChatCompletionAssistantMessageParam(
                        role="assistant", content=msg["content"]
                    )
                )
                for msg in history
            ]
        )

        try:
            response = await client.chat.completions.create(
                model=model, messages=messages
            )
            content = response.choices[0].message.content
            return self._clean_text(content or "")
        except Exception as e:
            raise LLMError(message=f"Failed to get LLM response: {str(e)}")

    async def analyze_grammar(
        self,
        history: List[Dict[str, str]],
        primary_language: str = "English",
        target_language: str = "Spanish",
    ) -> SessionAnalysis:
        """Analyze grammar and vocabulary from conversation history.

        Args:
            history: List of conversation turns.
            primary_language: User's native language for explanations.
            target_language: Language being learned for analysis.

        Returns:
            SessionAnalysis with summary and turn-by-turn feedback.

        Raises:
            LLMError: If analysis fails.
        """
        client, model = self._get_client()
        prompt = (
            "Analyze the user's grammar and vocabulary in the following conversation "
            f"where they are practicing {target_language}.\n\n"
            "IMPORTANT LANGUAGE REQUIREMENTS:\n"
            f'- The "summary" field MUST be in {primary_language}\n'
            f'- The "explanation" field in each feedback item MUST be in '
            f"{primary_language}\n"
            '- The "original_sentence" and "corrected_sentence" fields MUST be in '
            f"{target_language} (the language being learned)\n\n"
            "Return a JSON object with the following structure:\n"
            "{\n"
            f'    "summary": "Overall summary of performance in {primary_language}",\n'
            '    "feedback": [\n'
            "        {\n"
            '            "original_sentence": "User\'s exact original sentence with '
            f'error (in {target_language})",\n'
            '            "corrected_sentence": "Corrected user sentence (in '
            f'{target_language})",\n'
            '            "explanation": "Brief explanation of the error in '
            f'{primary_language}"\n'
            "        }\n"
            "    ]\n"
            "}\n"
            "Only include feedback for sentences that actually have errors or could "
            "be improved naturally.\n"
            'Focus on user messages (role: "user") when analyzing grammar.'
        )

        conversation_text = "\n".join([f"{h['role']}: {h['content']}" for h in history])

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": conversation_text},
                ],
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content or "{}")
            return SessionAnalysis(**data)
        except Exception as e:
            raise LLMError(message=f"Analysis failure: {str(e)}")


llm_service = LLMService()
