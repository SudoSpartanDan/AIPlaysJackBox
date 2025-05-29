import os
from typing import Optional

from loguru import logger
from openai import OpenAI

from ai_plays_jackbox.llm import ChatModel


class OpenAIModel(ChatModel):
    _model: str

    def __init__(self, model: str = "gpt-4o-mini"):
        self._open_ai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self._model = model

    def generate_text(
        self,
        prompt: str,
        instructions: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.5,
        top_p: float = 0.9,
    ) -> str:
        instructions_formatted = {"role": "developer", "content": instructions}
        chat_response = self._open_ai_client.chat.completions.create(
            model=self._model,
            messages=[instructions_formatted, {"role": "user", "content": prompt}],
            stream=False,
            max_completion_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        text = chat_response.choices[0].message.content.strip().replace("\n", " ")
        logger.info(f"Generated text: {text}")
        return text
