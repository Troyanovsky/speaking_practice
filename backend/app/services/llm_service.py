from typing import List, Dict
import json
from openai import AsyncOpenAI
from app.schemas.session import SessionAnalysis
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL
        )
        self.model = settings.LLM_MODEL

    async def generate_greeting(self, target_language: str, proficiency_level: str) -> str:
        """Generate an LLM-powered greeting that considers language and proficiency."""
        system_prompt = f"""You are a helpful language learning assistant for {target_language} at {proficiency_level} level.

Generate a friendly greeting that:
1. Welcomes the user warmly
2. Suggests a random conversation topic appropriate for their level
3. Asks an opening question to start the practice

Keep your response appropriate for a {proficiency_level} learner.

Respond in {target_language}. Keep the greeting concise (2-3 sentences)."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Generate a greeting to start the practice session."}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Greeting Generation Error: {e}")
            # Fallback to a simple greeting
            return f"Hello! Let's practice {target_language} today. What would you like to talk about?"

    async def get_response(self, history: List[Dict[str, str]], 
                           target_language: str = "English",
                           proficiency_level: str = "B1") -> str:
        """Get LLM response with user context for language and proficiency."""
        system_prompt = f"""You are a helpful language learning assistant helping a user practice {target_language} at {proficiency_level} level.

Adjust your language complexity to match their proficiency.

Keep your responses concise and natural. Encourage the user to speak more.
Respond in {target_language}."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I apologize, but I'm having trouble connecting to my brain right now."

    async def generate_summary(self, history: List[Dict[str, str]]) -> str:
        messages = [{"role": "system", "content": "Summarize the following conversation in 2-3 sentences."}]
        # Convert history dicts to string for summary context
        conversation_text = "\n".join([f"{h['role']}: {h['content']}" for h in history])
        messages.append({"role": "user", "content": conversation_text})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception:
            return "Summary unavailable."

    async def analyze_grammar(self, history: List[Dict[str, str]]) -> SessionAnalysis:
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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": conversation_text}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return SessionAnalysis(**data)
        except Exception as e:
            print(f"Analysis Error: {e}")
            # Fallback
            return SessionAnalysis(summary="Could not perform analysis.", feedback=[])

llm_service = LLMService()
