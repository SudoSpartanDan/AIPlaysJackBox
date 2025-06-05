from typing import Optional

from ai_plays_jackbox.bot.bot_base import JackBoxBotBase
from ai_plays_jackbox.bot.jackbox7.quiplash3 import Quiplash3Bot
from ai_plays_jackbox.llm.chat_model import ChatModel
from ai_plays_jackbox.llm.ollama_model import OllamaModel


class JackBoxBotFactory:
    @staticmethod
    def get_bot(
        room_type: str,
        name: str = "FunnyBot",
        personality: str = "You are the funniest bot ever.",
        chat_model: Optional[ChatModel] = None,
    ) -> JackBoxBotBase:
        if chat_model is None:
            chat_model = OllamaModel()
        if room_type == "quiplash3":
            return Quiplash3Bot(name=name, personality=personality, chat_model=chat_model)
        # elif room_type == "ridictionary":
        #     return DictionariumBot(name=name, personality=personality)
        # elif room_type == "patentlystupid":
        #     return PatentlyStupidBot(name=name, personality=personality, model=model)
        # elif room_type == "fourbage":
        #     return Fibbage4Bot(name=name, personality=personality, model=model)
        # elif room_type == "rapbattle":
        #     return MadVerseCityBot(name=name, personality=personality, model=model)
        else:
            raise ValueError(f"Unknown room type: {room_type}")
