import random

from loguru import logger

from ai_plays_jackbox.bot.jackbox6.bot_base import JackBox6BotBase

_DEFINITION_PROMPT_TEMPLATE = """
You are playing Dictionarium.

{prompt}

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be {max_length} characters or less.
- Do not include quotes in your response.
"""

_SYNONYM_PROMPT_TEMPLATE = """
You are playing Dictionarium.

{prompt}

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be {max_length} characters or less.
- Do not include quotes in your response.
"""

_SENTENCE_PROMPT_TEMPLATE = """
You are playing Dictionarium. You need to use a made up word in a sentence.

{prompt}

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be {max_length} characters or less.
- Do not include quotes in your response.
"""


class DictionariumBot(JackBox6BotBase):
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
        max_length = data.get("maxLength", 150)

        match room_state:
            case "EnterSingleText":
                entry = data.get("entry", None)
                entry_id = data.get("entryId", "")
                print(data)
                if not entry:
                    if entry_id == "Definition":
                        logger.info("Generating definition...")
                        template = _DEFINITION_PROMPT_TEMPLATE
                    elif entry_id == "Synonym":
                        logger.info("Generating synonym...")
                        template = _SYNONYM_PROMPT_TEMPLATE
                    elif entry_id == "Sentence":
                        logger.info("Generating sentence...")
                        template = _SENTENCE_PROMPT_TEMPLATE
                    else:
                        return

                    formatted_prompt = template.format(
                        personality=self._personality,
                        prompt=clean_prompt,
                        max_length=max_length,
                    )
                    submission = self._chat_model.generate_text(
                        formatted_prompt,
                        "",
                        temperature=self._chat_model._chat_model_temperature,
                        top_p=self._chat_model._chat_model_top_p,
                    )
                    submission = submission[: max_length - 1]
                    self._client_send({"action": "write", "entry": submission})

            case "MakeSingleChoice":
                choice_type = data.get("choiceType", "")
                if (
                    choice_type == "ChooseDefinition"
                    or choice_type == "ChooseSynonym"
                    or choice_type == "ChooseSentence"
                ):
                    choices: list[dict] = data.get("choices", [])
                    choice_indexes = [i for i in range(0, len(choices))]
                    selected_choice = random.choice(choice_indexes)
                    self._client_send({"action": "choose", "choice": selected_choice})

    def _handle_room_operation(self, data: dict):
        pass
