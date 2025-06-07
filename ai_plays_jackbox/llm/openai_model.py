import base64
import os
from typing import Optional

from loguru import logger
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionDeveloperMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.responses import Response

from ai_plays_jackbox.llm.chat_model import ChatModel


class OpenAIModel(ChatModel):
    _open_ai_client: OpenAI

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._open_ai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Check connection and if model exists, this will hard fail if connection can't be made
        # Or if the model is not found
        _ = self._open_ai_client.models.retrieve(self._model)

    @classmethod
    def get_default_model(cls):
        return "gpt-4o-mini"

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

        chat_response = self._open_ai_client.chat.completions.create(
            model=self._model,
            messages=[
                ChatCompletionDeveloperMessageParam(content=instructions, role="developer"),
                ChatCompletionUserMessageParam(content=prompt, role="user"),
            ],
            stream=False,
            max_completion_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        text = str(chat_response.choices[0].message.content).strip().replace("\n", "")
        logger.info(f"Generated text: {text}")
        return text

    def generate_sketch(
        self,
        prompt: str,
        instructions: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> bytes:
        image_gen_response: Response = self._open_ai_client.responses.create(
            model=self._model,
            instructions=instructions,
            input=prompt,
            temperature=temperature,
            top_p=top_p,
            tools=[
                {
                    "type": "image_generation",
                    "quality": "low",
                    "size": "1024x1024",
                }
            ],
        )
        # Save the image to a file
        image_data = [output.result for output in image_gen_response.output if output.type == "image_generation_call"]
        image_base64 = ""
        if image_data:
            image_base64 = str(image_data[0])

        return base64.b64decode(image_base64)
