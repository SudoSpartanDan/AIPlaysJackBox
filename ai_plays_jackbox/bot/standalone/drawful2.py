import random

from loguru import logger

from ai_plays_jackbox.bot.bot_base import JackBoxBotBase

_DRAWING_PROMPT_TEMPLATE = """
You are playing Drawful 2.

Generate an image with the following prompt: {prompt}

When generating your response, follow these rules:
- Your personality is: {personality}
- Make sure to implement your personality somehow into the drawing, but keep the prompt in mind
- The image must be a simple sketch
- The image must have a white background and use black for the lines
- Avoid intricate details
"""


class Drawful2Bot(JackBoxBotBase):
    _drawing_completed: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _player_operation_key(self) -> str:
        return f"player:{self._player_id}"

    def _is_player_operation_key(self, operation_key: str) -> bool:
        return operation_key == self._player_operation_key

    @property
    def _room_operation_key(self) -> str:
        return "room"

    def _is_room_operation_key(self, operation_key: str) -> bool:
        return operation_key == self._room_operation_key

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

        match room_state:
            case "Draw":
                colors = data.get("colors", ["#fb405a", "#7a2259"])
                selected_color = colors[0]
                canvas_height = int(data.get("size", {}).get("height", 320))
                canvas_width = int(data.get("size", {}).get("width", 320))
                lines = self._generate_drawing(prompt_text, canvas_height, canvas_width)
                object_key = data.get("objectKey", "")
                if object_key != "":
                    if not self._drawing_completed:
                        self._object_update(
                            object_key,
                            {
                                "lines": [{"color": selected_color, "thickness": 1, "points": l} for l in lines],
                                "submit": True,
                            },
                        )
                        # This prevents the bot from trying to draw multiple times
                        self._drawing_completed = True

            case "EnterSingleText":
                # We need to reset this once we're entering options
                self._drawing_completed = False
                # Listen, the bot can't see the drawing
                # so they're just going to say something
                text_key = data.get("textKey", "")
                self._text_update(text_key, self._generate_random_response())

            case "MakeSingleChoice":
                # Bot still can't see the drawing
                # so just pick something
                if data.get("type", "single") == "repeating":
                    pass
                choices = data.get("choices", [])
                choices_as_ints = [i for i in range(0, len(choices))]
                selected_choice = random.choice(choices_as_ints)
                self._client_send({"action": "choose", "choice": selected_choice})

    def _handle_room_operation(self, data: dict):
        pass

    def _generate_drawing(self, prompt: str, canvas_height: int, canvas_width: int) -> list[str]:
        logger.info("Generating drawing...")
        image_prompt = _DRAWING_PROMPT_TEMPLATE.format(prompt=prompt, personality=self._personality)
        image_bytes = self._chat_model.generate_sketch(
            image_prompt,
            "",
            temperature=self._chat_model._chat_model_temperature,
            top_p=self._chat_model._chat_model_top_p,
        )
        return self._image_bytes_to_polylines(image_bytes, canvas_height, canvas_width)

    def _generate_random_response(self) -> str:
        possible_responses = [
            "Abstract awkward silence",
            "Abstract existential dread",
            "Abstract late-stage capitalism",
            "Abstract lost hope",
            "Abstract the void",
            "Baby Yoda, but weird",
            "Barbie, but weird",
            "Confused dentist",
            "Confused gym teacher",
            "Confused lawyer",
            "Confused therapist",
            "DJ in trouble",
            "Definitely banana",
            "Definitely blob",
            "Definitely potato",
            "Definitely spaghetti",
            "Taylor Swift, but weird",
            "Waluigi, but weird",
            "banana with feelings",
            "chicken riding a scooter",
            "cloud with feelings",
            "confused gym teacher",
            "confused therapist",
            "dentist in trouble",
            "duck + existential dread",
            "duck riding a scooter",
            "excited janitor",
            "ferret + awkward silence",
            "giraffe + awkward silence",
            "giraffe filing taxes",
            "hamster + existential dread",
            "hamster + lost hope",
            "hamster riding a scooter",
            "janitor in trouble",
            "joyful octopus",
            "lawyer in trouble",
            "llama + awkward silence",
            "llama + late-stage capitalism",
            "lonely dentist",
            "lonely hamster",
            "lonely janitor",
            "lonely pirate",
            "mango with feelings",
            "pirate in trouble",
            "sad DJ",
            "sad hamster",
            "spaghetti with feelings",
            "terrified duck",
            "terrified ferret",
            "terrified lawyer",
        ]
        chosen_response = random.choice(possible_responses)
        return chosen_response
