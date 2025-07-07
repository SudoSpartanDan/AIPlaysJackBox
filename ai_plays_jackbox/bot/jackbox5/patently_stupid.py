import random
from typing import Optional

from loguru import logger

from ai_plays_jackbox.bot.jackbox5.bot_base import JackBox5BotBase

_ISSUE_PROMPT_PROMPT_TEMPLATE = """
You are playing Patently Stupid. You need to fill in the given prompt.

When generating your response, follow these rules:
- Your personality is: {personality}
- You response must be 45 letters or less.
- Do not include quotes in your response.
- Only fill in the blank; do not repeat the other parts of the prompt.

Fill in the blank:

{prompt}
"""

_SOLUTION_TITLE_PROMPT_TEMPLATE = """
You are playing Patently Stupid. The issue you are trying to solve is "{issue}"

I need you to generate a title for an invention that would solve the solution.

When generating your response, follow these rules:
- Your personality is: {personality}
- Your response must be 3 words or less.
- Do not include quotes in your response.
- Respond with only the title, nothing else. No newlines, etc.
"""

_SOLUTION_TAGLINE_PROMPT_TEMPLATE = """
You are playing Patently Stupid. The issue you are trying to solve is "{issue}" and the invention that is going to solve it is called "{title}"

I need you to generate a tagline for the invention.

When generating your response, follow these rules:
- Your personality is: {personality}
- Your response must be 30 characters or less.
- Do not include quotes in your response.
- Respond with only the tagline, nothing else. No newlines, etc.
"""

_SOLUTION_IMAGE_PROMPT_TEMPLATE = """
You are playing Patently Stupid. The issue you are trying to solve is "{issue}" and the invention that is going to solve it is called "{title}"

I need an drawing of this new invention.

When generating your response, follow these rules:
- The image must be a simple sketch
- The image must have a white background and use black for the lines
- Avoid intricate details
"""


class PatentlyStupidBot(JackBox5BotBase):
    _issue_to_solve: Optional[str] = None
    _solution_title: Optional[str] = None
    _solution_tagline: Optional[str] = None

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
        entry = data.get("entry")
        prompt: dict[str, str] = data.get("prompt", {})
        prompt_html = prompt.get("html", "")
        clean_prompt = self._html_to_text(prompt_html)
        choices: list[dict] = data.get("choices", [])

        if room_state == "EnterSingleText" and not bool(entry):
            if "Write a title" in clean_prompt:
                self._client_send({"action": "write", "entry": self._solution_title})
            if "Write a tagline" in clean_prompt:
                self._client_send({"action": "write", "entry": self._solution_tagline})
            if "Fill in the Blank" in clean_prompt:
                issue_fill_in = self._generate_issue(clean_prompt)
                self._client_send({"action": "write", "entry": issue_fill_in})

        elif room_state == "MakeSingleChoice":
            if "Present your idea!" in clean_prompt:
                done_text_html = data.get("doneText", {}).get("html", "")
                if done_text_html == "":
                    self._client_send({"action": "choose", "choice": 1})
            elif "Invest in the best!" in clean_prompt:
                filtered_choices = [c for c in choices if not c.get("disabled", True)]
                if filtered_choices:
                    choice = random.choice(filtered_choices)
                    self._client_send({"action": "choose", "choice": choice.get("index", 0)})
            elif "Press to skip this presentation." in clean_prompt:
                pass
            else:
                choice_indexes = [i for i in range(0, len(choices))]
                choice = random.choice(choice_indexes)  # type: ignore
                self._client_send({"action": "choose", "choice": choice})

        elif room_state == "Draw":
            logger.info(data)
            self._issue_to_solve = self._html_to_text(data["popup"]["html"])
            self._solution_title = self._generate_title()
            self._solution_tagline = self._generate_tagline()

            lines = self._generate_drawing()
            self._client_send(
                {
                    "action": "submit",
                    "lines": [{"color": "#000000", "thickness": 6, "points": l} for l in lines],
                },
            )

    def _handle_room_operation(self, data: dict):
        pass

    def _generate_issue(self, prompt: str) -> str:
        formatted_prompt = _ISSUE_PROMPT_PROMPT_TEMPLATE.format(personality=self._personality, prompt=prompt)
        issue = self._chat_model.generate_text(
            formatted_prompt,
            "",
            max_tokens=10,
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return issue

    def _generate_title(self) -> str:
        prompt = _SOLUTION_TITLE_PROMPT_TEMPLATE.format(personality=self._personality, issue=self._issue_to_solve)
        title = self._chat_model.generate_text(
            prompt,
            "",
            max_tokens=2,
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return title

    def _generate_tagline(self) -> str:
        prompt = _SOLUTION_TAGLINE_PROMPT_TEMPLATE.format(
            personality=self._personality, issue=self._issue_to_solve, title=self._solution_title
        )
        tagline = self._chat_model.generate_text(
            prompt,
            "",
            max_tokens=12,
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return tagline

    def _generate_drawing(self) -> list[str]:
        logger.info("Generating drawing...")
        image_prompt = _SOLUTION_IMAGE_PROMPT_TEMPLATE.format(issue=self._issue_to_solve, title=self._solution_title)
        image_bytes = self._chat_model.generate_sketch(
            image_prompt,
            "",
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return self._image_bytes_to_polylines(image_bytes, 475, 475)
