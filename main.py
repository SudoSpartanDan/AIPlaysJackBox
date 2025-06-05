from nicegui import ui

from ai_plays_jackbox import run
from ai_plays_jackbox.llm.ollama_model import OllamaModel
from ai_plays_jackbox.ui.create_ui import create_ui


def _get_room_code() -> str:
    while True:
        room_code = input("Please enter the room code: ")
        if len(room_code) != 4 or not room_code.isalpha():
            print("Invalid room code; please try again")
        else:
            return room_code.upper()


def main():
    room_code = _get_room_code()
    run(room_code, chat_model=OllamaModel(model="gemma3:12b"))


def run_ui():
    create_ui()
    ui.run()
