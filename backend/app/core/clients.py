import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)


    async def generate_new_word(self, system_prompt: str, user_prompt: str):
        contents = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_prompt)]
        )
        
        try:
            # Требуем от модели вернуть чистый JSON
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )

            result = json.loads(response.text)
            print(result)
            return result
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            # Возвращаем фоллбэк в случае сбоя AI
            return {
                "error": "Ошибка генерации нового слова"
            }
        