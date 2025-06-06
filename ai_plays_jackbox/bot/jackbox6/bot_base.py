from abc import ABC

from ai_plays_jackbox.bot.bot_base import JackBoxBotBase


class JackBox6BotBase(JackBoxBotBase, ABC):

    @property
    def _player_operation_key(self):
        return f"bc:customer:"

    def _is_player_operation_key(self, operation_key: str) -> bool:
        return self._player_operation_key in operation_key

    @property
    def _room_operation_key(self):
        return "bc:room"

    def _is_room_operation_key(self, operation_key: str) -> bool:
        return operation_key == self._room_operation_key
