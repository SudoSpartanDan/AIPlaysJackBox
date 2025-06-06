from abc import ABC

from ai_plays_jackbox.bot.bot_base import JackBoxBotBase


class JackBox7BotBase(JackBoxBotBase, ABC):

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
