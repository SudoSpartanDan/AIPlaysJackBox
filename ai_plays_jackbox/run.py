import itertools
import sys

from loguru import logger

from ai_plays_jackbox.llm import ChatModel, OllamaModel
from ai_plays_jackbox.room import JackBoxRoom


def run(room_code: str, num_of_bots: int = 4, chat_model: ChatModel = OllamaModel()):
    """Will run a set of bots through a game of JackBox given a room code.

    Args:
        room_code (str): The room code.
        num_of_bots (int, optional): The number of bots to participate. Defaults to 4.
        chat_model (ChatModel, optional): The chat model to use to generate responses. Defaults to OllamaModel().
    """
    _setup_logger()
    room = JackBoxRoom()
    room.play(room_code, num_of_bots=num_of_bots, chat_model=chat_model)


### I SPENT WAY TOO MUCH TIME DOING THIS FOR LOGGING

COLOR_CYCLE = itertools.cycle(["red", "green", "yellow", "blue", "magenta", "cyan", "white"])

# Global map of thread name → assigned color
assigned_colors = {}


def _get_next_color():
    return next(COLOR_CYCLE)


def _assign_color_to_thread(thread_name):
    if thread_name not in assigned_colors:
        assigned_colors[thread_name] = _get_next_color()
    return assigned_colors[thread_name]


def _format_log(record):
    thread_name = record["thread"].name
    color = _assign_color_to_thread(thread_name)
    colored_name = f"<{color}>{thread_name:<12}</{color}>"

    return (
        f"<green>{record['time']:YYYY-MM-DD HH:mm:ss}</green> | "
        f"<cyan>{record['level']:<8}</cyan> | "
        f"{colored_name} | "
        f"{record['message']}\n"
    )


def _setup_logger():
    logger.remove()  # Remove default handler
    logger.add(sink=sys.stdout, format=_format_log, level="INFO")
