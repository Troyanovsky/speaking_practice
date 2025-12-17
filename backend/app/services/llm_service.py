from typing import List, Dict
import json
from openai import AsyncOpenAI
from app.schemas.session import SessionAnalysis
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o" # Or gpt-3.5-turbo

    async def get_response(self, history: List[Dict[str, str]]) -> str:
        messages = [{"role": "system", "content": "You are a helpful language learning assistant. Keep your responses concise and natural. Encourage the user to speak."}]
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
