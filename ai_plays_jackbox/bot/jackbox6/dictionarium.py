import random

from loguru import logger

from ai_plays_jackbox.ai_prompter import get_ai_response
from ai_plays_jackbox.bot.jackbox6.bot_base import JackBox6BotBase

class DictionariumBot(JackBox6BotBase):
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
        entry = data.get("entry", None)
        entry_id = data.get("entryId", "")
        max_length = data.get("maxLength", 150)
        choice_type = data.get("choiceType", "")
        choices: list[dict] = data.get("choices", [])
        match room_state:
            case "EnterSingleText":
                if not entry:
                    if entry_id == "Definition":
                        submission = self._generate_definition(prompt_text)
                    elif entry_id == "Synonym":
                        submission = self._generate_synonym(prompt_text)
                    elif entry_id == "Sentence":
                        submission = self._generate_sentence(prompt_text)
                    submission = submission[:max_length]
                    self._write(submission)
            case "MakeSingleChoice":
                choice = None
                if choice_type == "ChooseDefinition" or choice_type == "ChooseSynonym":
                    choice = self._choose_favorite(prompt_text, choices)
                if choice is not None:
                    self._choose(choice)

        
    def _handle_room_operation(self, data: dict):
        pass

    def _write(self, text: str):
        self._client_send({"action": "write", "entry": text})

    def _choose(self, choice: int):
        self._client_send({"action": "choose", "choice": choice})

    def _generate_definition(self, prompt: str) -> str:
        formatted_prompt = _DEFINITION_PROMPT.format(personality=self._personality, prompt=prompt)
        definition = get_ai_response(formatted_prompt, num_predict=35)
        return definition
    
    def _generate_synonym(self, prompt: str) -> str:
        formatted_prompt = _SYNONYM_PROMPT.format(personality=self._personality, prompt=prompt)
        synonym = get_ai_response(formatted_prompt, num_predict=4)
        return synonym
    
    def _generate_sentence(self, prompt: str) -> str:
        formatted_prompt = _SENTENCE_PROMPT.format(personality=self._personality, prompt=prompt)
        sentence = get_ai_response(formatted_prompt, num_predict=35)
        return sentence

    def _choose_favorite(self, prompt: str, choices: list[dict]) -> int:
        choices_str = "\n".join([f"{i+1}. {v['html']}" for i, v in enumerate(choices)])
        formatted_prompt = _FAVORITE_CHOICE_PROMPT.format(prompt=prompt, options=choices_str)
        response = get_ai_response(prompt=formatted_prompt, num_predict=1)
        try:
            choosen_prompt = int(response)
        except ValueError:
            logger.warning(f"Can't choose favorite since response was not an int: {response}")
            return self._choose_random(choices)

        if choosen_prompt < 1 or choosen_prompt > len(choices):
            logger.warning(f"Can't choose favorite since response was not a valid value: {response}")
            return self._choose_random(choices)
        else:
            return choosen_prompt - 1
        
    def _choose_random(self, choices: list[dict]) -> int:
        choices = [i for i in range(0, len(choices))]
        return random.choice(choices)

_DEFINITION_PROMPT = """
You are playing Dictionarium. You need to create a definition for a word or phrase.

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be 100 characters or less.
- Do not include quotes in your response.

The prompt is:

{prompt}
"""

_FAVORITE_CHOICE_PROMPT = """
You are playing Dictionarium and you need to vote for your favorite response to the prompt {prompt}. Your options are:

{options}

Choose your favorite by responding with the number next to your choice. Only respond with the number and nothing else.
"""

_SYNONYM_PROMPT = """
You are playing Dictionarium. You need to create a synonym for a word or phrase.

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be 50 characters or less.
- Do not include quotes in your response.

The prompt is:

{prompt}
"""

_SENTENCE_PROMPT = """
You are playing Dictionarium. You need to use a made up word in a sentence.

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be 150 characters or less.
- Do not include quotes in your response.

The prompt is:

{prompt}
"""