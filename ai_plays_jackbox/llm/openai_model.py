import os
from typing import Optional

from loguru import logger
from openai import OpenAI

from ai_plays_jackbox.llm.chat_model import ChatModel


class OpenAIModel(ChatModel):
    _model: str
    _open_ai_client: OpenAI

    def __init__(self, model: str = "gpt-4o-mini", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._open_ai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self._model = model

        # Check connection, this will hard fail if connection can't be made
        _ = self._open_ai_client.models.list()

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

        instructions_formatted = {"role": "developer", "content": instructions}
        chat_response = self._open_ai_client.chat.completions.create(
            model=self._model,
            messages=[instructions_formatted, {"role": "user", "content": prompt}],
            stream=False,
            max_completion_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        text = chat_response.choices[0].message.content.strip().replace("\n", "")
        logger.info(f"Generated text: {text}")
        return text
