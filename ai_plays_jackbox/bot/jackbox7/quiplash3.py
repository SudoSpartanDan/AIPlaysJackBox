import random

from loguru import logger

from ai_plays_jackbox.bot.jackbox7.bot_base import JackBox7BotBase

_QUIP_PROMPT_INSTRUCTIONS_TEMPLATE = """
You are playing Quiplash 3. You need to fill in the given prompt.

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be 45 letters or less.
- Do not include quotes in your response.
"""

_FINAL_QUIP_PROMPT_INSTRUCTIONS_TEMPLATE = """
You are playing Quiplash 3 and it is the final round. The prompt will include three blanks, all of which you need to fill in.

When generating your response, follow these rules:
- Your personality is: {personality}
- Separate your answers by the character '|', for example 'Apple|Orange|Banana'.
- Each answer must be 45 letters or less.
- Do not include quotes in your response.
"""

_QUIP_CHOICE_PROMPT_INSTRUCTIONS_TEMPLATE = """
You are playing Quiplash 3 and you need to vote for your favorite response to the prompt "{prompt}".
Choose your favorite by responding with the number next to your choice. Only respond with the number and nothing else.
"""


class Quiplash3Bot(JackBox7BotBase):
    _selected_avatar: bool = False

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
        prompt = data.get("prompt")
        prompt_text = self._html_to_text(prompt.get("html", "")) if prompt is not None else ""
        text_key = data.get("textKey", "")
        match room_state:
            case "EnterSingleText":
                if not data["entry"]:
                    quip = self._generate_quip(prompt_text)
                    self._send_ws("text/update", {"key": text_key, "val": quip})
            case "EnterTextList":
                if not data["entries"]:
                    quip = self._generate_quip(prompt_text, final_round=True)
                    self._send_ws("text/update", {"key": text_key, "val": "\n".join(quip.split("|"))})
            case "MakeSingleChoice":
                choice = self._choose_favorite(prompt_text, data["choices"])
                self._client_send({"action": "choose", "choice": choice})

    def _handle_room_operation(self, data: dict):
        if self._selected_avatar:
            return
        available_characters = [c["name"] for c in data["characters"] if c["available"]]
        selected_character = random.choice(available_characters)
        self._client_send({"action": "avatar", "name": selected_character})
        self._selected_avatar = True

    def _generate_quip(self, prompt: str, final_round: bool = False) -> str:
        max_tokens = 10
        instructions = _QUIP_PROMPT_INSTRUCTIONS_TEMPLATE.format(personality=self._personality)
        if final_round:
            max_tokens = 32
            instructions = _FINAL_QUIP_PROMPT_INSTRUCTIONS_TEMPLATE.format(personality=self._personality)
        quip = self._chat_model.generate_text(
            prompt,
            instructions,
            max_tokens=max_tokens,
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return quip

    def _choose_favorite(self, prompt: str, choices: list[dict]) -> int:
        choices_str = "\n".join([f"{i+1}. {v['html']}" for i, v in enumerate(choices)])
        instructions = _QUIP_CHOICE_PROMPT_INSTRUCTIONS_TEMPLATE.format(prompt=prompt)
        response = self._chat_model.generate_text(
            f"Vote for your favorite response. Your options are: {choices_str}",
            instructions,
            max_tokens=1,
        )
        try:
            choosen_prompt = int(response)
        except ValueError:
            logger.warning(f"Can't choose favorite since response was not an int: {response}")
            return self._choose_random_favorite(choices)

        if choosen_prompt < 1 or choosen_prompt > len(choices):
            logger.warning(f"Can't choose favorite since response was not a valid value: {response}")
            return self._choose_random_favorite(choices)
        else:
            return choosen_prompt - 1

    def _choose_random_favorite(self, choices: list[dict]) -> int:
        choices_as_ints = [i for i in range(0, len(choices))]
        return random.choice(choices_as_ints)
