from typing import List, Dict
import json
import re
from openai import AsyncOpenAI
from app.schemas.session import SessionAnalysis
from app.core.config import settings
from app.core.topics import get_topic_for_level

from app.services.settings_service import settings_service

from app.core.exceptions import LLMError

class LLMService:
    def __init__(self):
        # Client is now created dynamically per request to support setting changes
        pass

    def _get_client(self):
        user_settings = settings_service.get_settings()
        client = AsyncOpenAI(
            api_key=user_settings.llm_api_key,
            base_url=user_settings.llm_base_url
        )
        return client, user_settings.llm_model

    def _clean_text(self, text: str) -> str:
        """Remove markdown formatting characters and normalize whitespace."""
        # Remove code blocks and inline code (do this first)
        text = re.sub(r'`{1,3}.*?`{1,3}', '', text, flags=re.DOTALL)
        # Remove bold/italic markers
        text = re.sub(r'[*_]{1,3}', '', text)
        # Remove markdown links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove list markers at start of lines or after whitespace
        text = re.sub(r'(?m)^\s*[-+*]\s+', '', text)
        text = re.sub(r'(?m)^\s*\d+\.\s+', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def generate_greeting(self, target_language: str, proficiency_level: str, primary_language: str = "English") -> str:
        """Generate an LLM-powered greeting that considers language and proficiency."""
        client, model = self._get_client()
        
        # Get a predefined topic for the proficiency level
        topic = get_topic_for_level(proficiency_level)
        
        system_prompt = f"""You are a helpful language learning assistant for {target_language} at {proficiency_level} level. Your name is Luna.
        
Generate a friendly greeting that:
1. Welcomes the user warmly
2. Suggests the following conversation topic: "{topic}"
3. Asks an opening question to start the practice

Keep your response appropriate for a {proficiency_level} learner. Keep the greeting short and to the point.

CRITICAL: You MUST respond EXCLUSIVELY in {target_language}. All parts of your response (greeting, topic suggestion, and question) must be in {target_language}. Keep the greeting concise (2-3 sentences).

DO NOT use any markdown formatting such as bold (**text**), italics (*text*), or lists. Return only pure text sentences."""

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate a greeting to start the practice session in {target_language} about the topic: {topic}"}
                ]
            )
            content = response.choices[0].message.content
            return self._clean_text(content)
        except Exception as e:
            raise LLMError(message=f"Greeting generation failed: {str(e)}")

    async def get_response(self, history: List[Dict[str, str]], 
                           target_language: str = "English",
                           proficiency_level: str = "B1") -> str:
        """Get LLM response with user context for language and proficiency."""
        client, model = self._get_client()
        
        system_prompt = f"""You are a helpful language learning assistant named Luna, helping a user practice {target_language} at {proficiency_level} level.

Adjust your language complexity to match their proficiency.

Keep your responses concise (2-3 sentences max) and natural (as if talking to a friend). Encourage the user to speak more.
CRITICAL: You MUST respond EXCLUSIVELY in {target_language}. Do not use any other language.

DO NOT use any markdown formatting such as bold (**text**), italics (*text*), or lists. Return only pure text sentences."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages
            )
            content = response.choices[0].message.content
            return self._clean_text(content)
        except Exception as e:
            raise LLMError(message=f"Failed to get LLM response: {str(e)}")

    async def analyze_grammar(self, history: List[Dict[str, str]], primary_language: str = "English") -> SessionAnalysis:
        client, model = self._get_client()
        prompt = f"""
        Analyze the user's grammar and vocabulary in the following conversation.
        Provide your analysis and feedback in {primary_language}.
        Return a JSON object with the following structure:
        {{
            "summary": "Overall summary of performance in {primary_language}",
            "feedback": [
                {{
                    "original_sentence": "User's exact original sentence with error",
                    "corrected_sentence": "Corrected user sentence",
                    "explanation": "Brief explanation of the error in {primary_language}"
                }}
            ]
        }}
        Only include feedback for sentences that actually have errors or could be improved naturally.
        Make sure all explanations are in {primary_language}.
        """
        
        conversation_text = "\n".join([f"{h['role']}: {h['content']}" for h in history])
        
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": conversation_text}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return SessionAnalysis(**data)
        except Exception as e:
            raise LLMError(message=f"Analysis failure: {str(e)}")

llm_service = LLMService()
