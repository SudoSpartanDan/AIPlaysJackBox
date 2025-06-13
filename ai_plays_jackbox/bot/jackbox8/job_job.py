import random
import string

from loguru import logger

from ai_plays_jackbox.bot.jackbox8.bot_base import JackBox8BotBase

_RESPONSE_PROMPT_TEMPLATE = """
You are playing Job Job. You need response to the given prompt.

When generating your response, follow these rules:
- Your personality is: {personality}
- Your response must be {max_length} letters or less.
- Your response must have a minimum of {min_words} words.
- Do not include quotes in your response.

{instruction}

Your prompt is:

{prompt}
"""

_COMPOSITION_PROMPT_TEMPLATE = """
You are playing Job Job. You must create a response to a interview question using only specific words given.

When generating your response, follow these rules:
- Your personality is: {personality}
- Your response must only use the allowed words or characters, nothing else
- If you decide to use a character, you must have it separated by a space from any words
- You can select a maximum of {max_words} words

Your interview question is:

{prompt}

Your allowed words or characters are:

{all_possible_words_str}
"""


class JobJobBot(JackBox8BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _handle_welcome(self, data: dict):
        pass

    def _handle_player_operation(self, data: dict):
        if not data:
            return

        kind = data.get("kind", "")
        has_controls = data.get("hasControls", False)
        response_key = data.get("responseKey", "")
        done_key = data.get("doneKey", "")

        if has_controls:
            if "skip:" in response_key:
                self._object_update(response_key, {"action": "skip"})
                return

        match kind:
            case "writing":
                instruction = data.get("instruction", "")
                prompt = data.get("prompt", "")
                max_length = data.get("maxLength", 128)
                min_words = data.get("minWords", 5)
                text_key = data.get("textKey", "")
                response = self._generate_response(instruction, prompt, max_length, min_words)
                self._text_update(text_key, response)
                self._object_update(done_key, {"done": True})

            case "magnets":
                prompt = data.get("prompt", "")
                answer_key = data.get("answerKey", "")
                stash = data.get("stash", [[]])
                max_words = data.get("maxWords", 12)
                composition_list = self._generate_composition_list(prompt, stash, max_words)
                self._object_update(
                    answer_key,
                    {
                        "final": True,
                        "text": composition_list,
                    },
                )

            case "resumagents":
                prompt = data.get("prompt", "")
                answer_key = data.get("answerKey", "")
                stash = data.get("stash", [[]])
                max_words = data.get("maxWords", 12)
                max_words_per_answer = data.get("maxWordsPerAnswer", 8)
                num_answers = data.get("numAnswers", 8)
                resume_composition_list = self._generate_resume_composition_list(
                    prompt, stash, max_words, max_words_per_answer, num_answers
                )
                self._object_update(
                    answer_key,
                    {
                        "final": True,
                        "text": resume_composition_list,
                    },
                )

            case "voting":
                choices: list[dict] = data.get("choices", [])
                choice_indexes = [i for i in range(0, len(choices))]
                selected_choice = random.choice(choice_indexes)
                self._object_update(response_key, {"action": "choose", "choice": selected_choice})

    def _handle_room_operation(self, data: dict):
        pass

    def _generate_response(self, instruction: str, prompt: str, max_length: int, min_words: int) -> str:
        formatted_prompt = _RESPONSE_PROMPT_TEMPLATE.format(
            personality=self._personality,
            max_length=max_length,
            min_words=min_words,
            instruction=instruction,
            prompt=prompt,
        )
        response = self._chat_model.generate_text(
            formatted_prompt,
            "",
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        if len(response) > max_length:
            response = response[: max_length - 1]
        return response

    def _generate_composition_list(
        self,
        prompt: str,
        stash: list[list[str]],
        max_words: int,
    ) -> list[dict]:

        possible_word_choices = []

        for stash_entry in stash:
            for word in stash_entry:
                possible_word_choices.append(word)

        all_possible_words_str = "\n".join([word for word in possible_word_choices])
        formatted_prompt = _COMPOSITION_PROMPT_TEMPLATE.format(
            personality=self._personality,
            all_possible_words_str=all_possible_words_str,
            max_words=max_words,
            prompt=prompt,
        )
        response = self._chat_model.generate_text(
            formatted_prompt,
            "",
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )

        ## Listen, I know this is isn't the fastest way to search
        ## It's 12 words, bite me with your Big O notation
        composition_list = []
        response_list = response.split(" ")
        for response_word in response_list:
            found_word = False
            response_word = response_word.strip()
            if not all(char in string.punctuation for char in response_word):
                response_word = response_word.translate(str.maketrans("", "", string.punctuation)).lower()

            if not found_word:
                for stash_index, stash_entry in enumerate(stash):
                    for check_word_index, check_word in enumerate(stash_entry):
                        if response_word == check_word.lower():
                            composition_list.append(
                                {
                                    "index": stash_index,
                                    "word": check_word_index,
                                }
                            )
                            found_word = True
                            break
                    if found_word:
                        break

            if not found_word:
                logger.warning(f"Word not found in choices: {response_word}")

        if len(composition_list) > max_words:
            composition_list = composition_list[: max_words - 1]
        return composition_list

    def _generate_resume_composition_list(
        self,
        prompt: str,
        stash: list[list[str]],
        max_words: int,
        max_words_per_answers: int,
        num_of_answers: int,
    ) -> list[list[dict]]:
        # TODO Figure this out
        resume_composition_list = []
        for _ in range(0, num_of_answers):
            resume_composition_list.append([{"index": 0, "word": 0}])
        return resume_composition_list
