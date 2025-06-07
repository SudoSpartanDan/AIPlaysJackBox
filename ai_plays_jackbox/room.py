import random
import threading
from time import sleep
from typing import Optional

import requests
from loguru import logger

from ai_plays_jackbox.bot.bot_base import JackBoxBotBase
from ai_plays_jackbox.bot.bot_factory import JackBoxBotFactory
from ai_plays_jackbox.bot.bot_personality import JackBoxBotVariant
from ai_plays_jackbox.constants import ECAST_HOST
from ai_plays_jackbox.llm.chat_model import ChatModel


class JackBoxRoom:
    _bots: list[JackBoxBotBase]

    def __init__(self):
        self._bots = []
        self._lock = threading.Lock()

    def play(
        self,
        room_code: str,
        chat_model: ChatModel,
        num_of_bots: int = 4,
        bots_in_play: Optional[list] = None,
    ):
        room_type = self._get_room_type(room_code)
        if not room_type:
            logger.error(f"Unable to find room {room_code}")
            return
        logger.info(f"We're playing {room_type}!")
        bot_factory = JackBoxBotFactory()
        if bots_in_play is None or len(bots_in_play) == 0:
            bots_to_make = random.sample(list(JackBoxBotVariant), num_of_bots)
        else:
            bots_in_play_variants = [variant for variant in JackBoxBotVariant if variant.name in bots_in_play]
            bots_to_make = random.choices(bots_in_play_variants, k=num_of_bots)

        for b in bots_to_make:
            bot = bot_factory.get_bot(
                room_type,
                chat_model,
                name=b.value.name,
                personality=b.value.personality,
            )
            self._bots.append(bot)
            with self._lock:
                bot.connect(room_code)
            sleep(0.5)

        try:
            while True:
                sleep(1)
                if self.is_finished():
                    print("All bots disconnected, ending...")
                    break
        except KeyboardInterrupt:
            self.end()

    def is_finished(self) -> bool:
        for b in self._bots:
            if not b.is_disconnected():
                return False
        return True

    def end(self):
        for b in self._bots:
            with self._lock:
                b.disconnect()

    def _get_room_type(self, room_code: str) -> str:
        try:
            response = requests.request(
                "GET",
                f"https://{ECAST_HOST}/api/v2/rooms/{room_code}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0"},
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.HTTPError:
            if response.status_code != 404:
                logger.error(f"Received {response.status_code} when trying to get room type.")
            return ""
        return response_data["body"]["appTag"]
