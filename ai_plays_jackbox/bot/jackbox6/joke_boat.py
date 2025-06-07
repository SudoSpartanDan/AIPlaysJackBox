import random

from loguru import logger

from ai_plays_jackbox.bot.jackbox6.bot_base import JackBox6BotBase

_TOPIC_PROMPT_TEMPLATE = """
You are playing Joke Boat.

You are being asked to come up with a topic that is {placeholder}.

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be {max_length} characters or less
- Your response should be a single word.
- Do not include quotes in your response or any newlines, just the response itself
"""

_PUNCHLINE_INSTRUCTIONS_TEMPLATE = """
You are playing Joke Boat. You need to fill in the given prompt with a punchline.

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be {max_length} characters or less
- Do not include quotes in your response or any newlines, just the response itself
"""


class JokeBoatBot(JackBox6BotBase):
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

        prompt = data.get("prompt", {})
        prompt_html = prompt.get("html", "")
        clean_prompt = self._html_to_text(prompt_html)

        match room_state:
            case "MakeSingleChoice":
                choices: list[dict] = data.get("choices", [])
                choice_type = data.get("choiceType", "")
                choice_indexes = [i for i in range(0, len(choices))]
                selected_choice = random.choice(choice_indexes)

                if choice_type == "ChooseAuthorReady":
                    selected_choice = 1
                if choice_type == "Skip":
                    selected_choice = 0

                if data.get("chosen", None) is None:
                    self._client_send({"action": "choose", "choice": selected_choice})

            case "EnterSingleText":
                if "Write as many topics as you can." in clean_prompt:
                    placeholder = data.get("placeholder", "")
                    max_length = data.get("maxLength", 42)
                    topic = self._generate_topic(placeholder, max_length)
                    self._client_send({"action": "write", "entry": topic})
                if "Write your punchline" in clean_prompt or "Write the punchline to this joke" in clean_prompt:
                    max_length = data.get("maxLength", 80)
                    punchline = self._generate_punchline(clean_prompt, max_length)
                    self._client_send({"action": "write", "entry": punchline})

    def _handle_room_operation(self, data: dict):
        pass

    def _generate_topic(self, placeholder: str, max_length: int) -> str:
        logger.info("Generating topic...")
        formatted_prompt = _TOPIC_PROMPT_TEMPLATE.format(
            personality=self._personality,
            placeholder=placeholder,
            max_length=max_length,
        )

        topic = self._chat_model.generate_text(
            formatted_prompt,
            "",
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return topic[:max_length]

    def _generate_punchline(self, prompt: str, max_length: int) -> str:
        logger.info("Generating punchline...")
        formatted_instructions = _PUNCHLINE_INSTRUCTIONS_TEMPLATE.format(
            personality=self._personality,
            prompt=prompt,
            max_length=max_length,
        )
        punchline = self._chat_model.generate_text(
            prompt,
            formatted_instructions,
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return punchline[:max_length]
