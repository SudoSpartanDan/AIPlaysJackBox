from abc import ABC
from typing import Optional

from ai_plays_jackbox.bot.bot_base import JackBoxBotBase


class JackBox5BotBase(JackBoxBotBase, ABC):
    _actual_player_operation_key: Optional[str] = None

    @property
    def _player_operation_key(self):
        return f"bc:customer:"

    def _is_player_operation_key(self, operation_key: str) -> bool:
        if self._actual_player_operation_key is None and self._player_operation_key in operation_key:
            self._actual_player_operation_key = operation_key
            return True
        else:
            return self._actual_player_operation_key == operation_key

    @property
    def _room_operation_key(self):
        return "bc:room"

    def _is_room_operation_key(self, operation_key: str) -> bool:
        return operation_key == self._room_operation_key
