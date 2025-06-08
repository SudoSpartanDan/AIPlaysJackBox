from typing import Optional

from ai_plays_jackbox.llm.chat_model_factory import ChatModelFactory
from ai_plays_jackbox.room.room import JackBoxRoom


def run(
    room_code: str,
    chat_model_provider: str,
    chat_model_name: Optional[str] = None,
    num_of_bots: int = 4,
    bots_in_play: Optional[list] = None,
    chat_model_temperature: float = 0.5,
    chat_model_top_p: float = 0.9,
):
    chat_model = ChatModelFactory.get_chat_model(
        chat_model_provider,
        chat_model_name=chat_model_name,
        chat_model_temperature=chat_model_temperature,
        chat_model_top_p=chat_model_top_p,
    )
    room = JackBoxRoom()
    room.play(room_code, chat_model, num_of_bots=num_of_bots, bots_in_play=bots_in_play)
