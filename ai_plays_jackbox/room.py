from time import sleep

import requests
from loguru import logger
import random

from ai_plays_jackbox.bot.bot_base import JackBoxBotBase
from ai_plays_jackbox.bot.bot_factory import JackBoxBotFactory
from ai_plays_jackbox.constants import ECAST_HOST
from ai_plays_jackbox.bot.bot_personality import JackBoxBotVariant


class JackBoxRoom:
    _bots: list[JackBoxBotBase] = []

    def play(self, room_code: str, num_of_bots: int = 4):
        room_type = self._get_room_type(room_code)
        logger.info(f"We're playing {room_type}!")
        bot_factory = JackBoxBotFactory()
        bots_to_make = random.sample(list(JackBoxBotVariant), num_of_bots)

        for b in bots_to_make:
            bot = bot_factory.get_bot(
                room_type,
                name=b.value.name,
                personality=b.value.personality,
            )
            self._bots.append(bot)
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
            b.disconnect()

    def _get_room_type(self, room_code: str):
        response = requests.request(
            "GET",
            f"https://{ECAST_HOST}/api/v2/rooms/{room_code}",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0"},
        )
        response.raise_for_status()
        response_data = response.json()
        return response_data["body"]["appTag"]
