from ai_plays_jackbox.bot.bot_base import JackBoxBotBase
from ai_plays_jackbox.bot.jackbox5.mad_verse_city import MadVerseCityBot
from ai_plays_jackbox.bot.jackbox5.patently_stupid import PatentlyStupidBot
from ai_plays_jackbox.bot.jackbox6.dictionarium import DictionariumBot
from ai_plays_jackbox.bot.jackbox6.joke_boat import JokeBoatBot
from ai_plays_jackbox.bot.jackbox7.quiplash3 import Quiplash3Bot
from ai_plays_jackbox.bot.standalone.drawful2 import Drawful2Bot
from ai_plays_jackbox.llm.chat_model import ChatModel

BOT_TYPES: dict[str, type[JackBoxBotBase]] = {
    "quiplash3": Quiplash3Bot,
    "patentlystupid": PatentlyStupidBot,
    "drawful2international": Drawful2Bot,
    "rapbattle": MadVerseCityBot,
    "jokeboat": JokeBoatBot,
    "ridictionary": DictionariumBot,
    # "apply-yourself": JobJobBot,
}


class JackBoxBotFactory:
    @staticmethod
    def get_bot(
        room_type: str,
        chat_model: ChatModel,
        name: str = "FunnyBot",
        personality: str = "You are the funniest bot ever.",
    ) -> JackBoxBotBase:
        if room_type not in BOT_TYPES.keys():
            raise ValueError(f"Unknown room type: {room_type}")
        return BOT_TYPES[room_type](name=name, personality=personality, chat_model=chat_model)
