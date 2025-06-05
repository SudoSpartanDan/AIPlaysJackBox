from typing import Optional

from ai_plays_jackbox.llm.chat_model_factory import ChatModelFactory
from ai_plays_jackbox.room import JackBoxRoom


def run(
    room_code: str,
    num_of_bots: int = 4,
    bots_in_play: Optional[list] = None,
    chat_model_name: str = "ollama",
    chat_model_temperature: float = 0.5,
    chat_model_top_p: float = 0.9,
):
    """Will run a set of bots through a game of JackBox given a room code.

    Args:
        room_code (str): The room code.
        num_of_bots (int, optional): The number of bots to participate. Defaults to 4.
        chat_model (str, optional): The chat model to use to generate responses. Defaults to "ollama".
    """
    chat_model = ChatModelFactory.get_chat_model(
        chat_model_name, chat_model_temperature=chat_model_temperature, chat_model_top_p=chat_model_top_p
    )
    room = JackBoxRoom()
    room.play(room_code, num_of_bots=num_of_bots, bots_in_play=bots_in_play, chat_model=chat_model)
