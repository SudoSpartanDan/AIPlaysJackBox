import random
from typing import Optional

import demoji
from loguru import logger

from ai_plays_jackbox.bot.jackbox5.bot_base import JackBox5BotBase

_WORD_PROMPT_TEMPLATE = """
You are playing Mad Verse City. You are being asked to come up with a word.

{prompt}

When generating your response, follow these rules:
- You response must be {max_length} characters or less. It must be a singular word
- Your personality is: {personality}
- Do not include quotes in your response or any newlines, just the response itself.
- Some suggestions for the word are {suggestions}
"""

_RHYME_PROMPT_TEMPLATE = """
You are playing Mad Verse City.

{prompt}

When generating your response, follow these rules:
- Your response must rhyme with {rhyme_word}. It cannot be the same word as that.
- You response must be {max_length} characters or less.
- Your personality is: {personality}
- Do not include quotes in your response or any newlines, just the response itself.
"""


class MadVerseCityBot(JackBox5BotBase):
    _actual_player_operation_key: Optional[str] = None
    _current_word: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _handle_welcome(self, data: dict):
        pass

    def _handle_player_operation(self, data: dict):
        if not data:
            return
        room_state = data.get("state", None)
        if not room_state:
            return

        prompt: dict[str, str] = data.get("prompt", {})
        prompt_html = prompt.get("html", "")
        clean_prompt = self._html_to_text(prompt_html)

        max_length = data.get("maxLength", 40)
        suggestions = data.get("suggestions", [])
        if not suggestions:
            suggestions = []
        choices: list[dict] = data.get("choices", [])

        match room_state:
            case "EnterSingleText":
                if "Give me a" in clean_prompt:
                    word = self._generate_word(clean_prompt, max_length - 10, suggestions)
                    self._current_word = demoji.replace(word, "")
                    self._client_send({"action": "write", "entry": word})

                if "Now, write a line to rhyme with" in clean_prompt:
                    rhyme = self._generate_rhyme(clean_prompt, max_length - 10, self._current_word)
                    rhyme = demoji.replace(rhyme, "")
                    self._client_send({"action": "write", "entry": rhyme})

            case "MakeSingleChoice":
                if not choices:
                    pass
                if "Who won this battle" in data.get("prompt", {}).get("text", "") and data.get("chosen", None) != 0:
                    choice_indexes = [i for i in range(0, len(choices))]
                    choice = random.choice(choice_indexes)
                    self._client_send({"action": "choose", "choice": choice})

                if (
                    "Press this button to skip the tutorial" in data.get("prompt", {}).get("text", "")
                    and data.get("chosen", None) != 0
                ):
                    self._client_send({"action": "choose", "choice": 0})

    def _handle_room_operation(self, data: dict):
        pass

    def _generate_word(self, prompt: str, max_length: int, suggestions: list[str]) -> str:
        logger.info("Generating word...")
        formatted_prompt = _WORD_PROMPT_TEMPLATE.format(
            personality=self._personality,
            prompt=prompt,
            max_length=max_length,
            suggestions=", ".join(suggestions),
        )

        word = self._chat_model.generate_text(
            formatted_prompt,
            "",
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return word

    def _generate_rhyme(self, prompt: str, max_length: int, rhyme_word: str) -> str:
        logger.info("Generating rhyme...")
        formatted_prompt = _RHYME_PROMPT_TEMPLATE.format(
            personality=self._personality,
            prompt=prompt,
            max_length=max_length,
            rhyme_word=rhyme_word,
        )
        rhyme = self._chat_model.generate_text(
            formatted_prompt,
            "",
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return rhyme
