import os
from typing import Optional

from google import genai
from google.genai.types import GenerateContentConfig
from loguru import logger

from ai_plays_jackbox.llm.chat_model import ChatModel


class GeminiModel(ChatModel):
    _gemini_vertex_ai_client: genai.Client

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gemini_vertex_ai_client = genai.Client(
            vertexai=bool(os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")),
            api_key=os.environ.get("GOOGLE_GEMINI_DEVELOPER_API_KEY"),
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION"),
        )

        # Check connection and if model exists, this will hard fail if connection can't be made
        # Or if the model is not found
        _ = self._gemini_vertex_ai_client.models.get(self._model)

    @classmethod
    def get_default_model(cls):
        return "gemini-2.0-flash-001"

    def generate_text(
        self,
        prompt: str,
        instructions: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        if temperature is None:
            temperature = self._chat_model_temperature
        if top_p is None:
            top_p = self._chat_model_top_p

        chat_response = self._gemini_vertex_ai_client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=GenerateContentConfig(
                system_instruction=[instructions],
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            ),
        )

        text = str(chat_response.text).strip().replace("\n", "")
        logger.info(f"Generated text: {text}")
        return text
