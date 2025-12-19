from typing import List, Dict
import json
from openai import AsyncOpenAI
from app.schemas.session import SessionAnalysis
from app.core.config import settings

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

    async def generate_greeting(self, target_language: str, proficiency_level: str) -> str:
        """Generate an LLM-powered greeting that considers language and proficiency."""
        client, model = self._get_client()
        
        system_prompt = f"""You are a helpful language learning assistant for {target_language} at {proficiency_level} level.

Generate a friendly greeting that:
1. Welcomes the user warmly
2. Suggests a random conversation topic appropriate for their level
3. Asks an opening question to start the practice

Keep your response appropriate for a {proficiency_level} learner.

Respond in {target_language}. Keep the greeting concise (2-3 sentences)."""

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Generate a greeting to start the practice session."}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMError(message=f"Greeting generation failed: {str(e)}")

    async def get_response(self, history: List[Dict[str, str]], 
                           target_language: str = "English",
                           proficiency_level: str = "B1") -> str:
        """Get LLM response with user context for language and proficiency."""
        client, model = self._get_client()
        
        system_prompt = f"""You are a helpful language learning assistant helping a user practice {target_language} at {proficiency_level} level.

Adjust your language complexity to match their proficiency.

Keep your responses concise and natural. Encourage the user to speak more.
Respond in {target_language}."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMError(message=f"Failed to get LLM response: {str(e)}")

    async def generate_summary(self, history: List[Dict[str, str]]) -> str:
        client, model = self._get_client()
        messages = [{"role": "system", "content": "Summarize the following conversation in 2-3 sentences."}]
        # Convert history dicts to string for summary context
        conversation_text = "\n".join([f"{h['role']}: {h['content']}" for h in history])
        messages.append({"role": "user", "content": conversation_text})

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMError(message=f"Summary generation failed: {str(e)}")

    async def analyze_grammar(self, history: List[Dict[str, str]]) -> SessionAnalysis:
        client, model = self._get_client()
        prompt = """
        Analyze the user's grammar and vocabulary in the following conversation.
        Return a JSON object with the following structure:
        {
            "summary": "Overall summary of performance",
            "feedback": [
                {
                    "original_sentence": "User's sentence with error",
                    "corrected_sentence": "Corrected user sentence",
                    "explanation": "Brief explanation of the error"
                }
            ]
        }
        Only include feedback for sentences that actually have errors or could be improved naturally.
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
