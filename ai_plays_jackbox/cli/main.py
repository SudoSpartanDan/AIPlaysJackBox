import argparse

from ai_plays_jackbox.bot.bot_personality import JackBoxBotVariant
from ai_plays_jackbox.constants import (
    DEFAULT_NUM_OF_BOTS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
)
from ai_plays_jackbox.llm.chat_model_factory import CHAT_MODEL_PROVIDERS
from ai_plays_jackbox.run import run


def _validate_room_code(string_to_check: str) -> str:
    if not string_to_check.isalpha() or len(string_to_check) != 4:
        raise argparse.ArgumentTypeError("Must be 4 letters")
    return string_to_check


def _validate_num_of_bots(string_to_check: str) -> int:
    try:
        number_value = int(string_to_check)
    except ValueError:
        raise argparse.ArgumentTypeError("Must number 1-10")
    if number_value < 1 or number_value > 10:
        raise argparse.ArgumentTypeError("Must number 1-10")
    return number_value


def _validate_temperature(string_to_check: str) -> float:
    try:
        number_value = float(string_to_check)
    except ValueError:
        raise argparse.ArgumentTypeError("Must number 0.1-2.0")
    if number_value <= 0 or number_value > 2.0:
        raise argparse.ArgumentTypeError("Must number 0.1-2.0")
    return number_value


def _validate_top_p(string_to_check: str) -> float:
    try:
        number_value = float(string_to_check)
    except ValueError:
        raise argparse.ArgumentTypeError("Must number 0.0-1.0")
    if number_value < 0 or number_value > 1.0:
        raise argparse.ArgumentTypeError("Must number 0.0-1.0")
    return number_value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--room-code",
        required=True,
        help="The JackBox room code",
        type=_validate_room_code,
        metavar="WXYZ",
    )
    parser.add_argument(
        "--chat-model-provider",
        required=True,
        help="Choose which chat model platform to use",
        choices=list(CHAT_MODEL_PROVIDERS.keys()),
        type=str,
    )
    parser.add_argument(
        "--chat-model-name",
        required=False,
        help="Choose which chat model to use (Will default to default for provider)",
        type=str,
    )
    parser.add_argument(
        "--num-of-bots",
        required=False,
        default=DEFAULT_NUM_OF_BOTS,
        help="How many bots to have play",
        type=_validate_num_of_bots,
        metavar=str(DEFAULT_NUM_OF_BOTS),
    )
    parser.add_argument(
        "--bots-in-play",
        required=False,
        nargs="*",
        help="Which bots are in play?",
        choices=[variant.name for variant in JackBoxBotVariant],
        type=str,
    )
    parser.add_argument(
        "--temperature",
        required=False,
        default=DEFAULT_TEMPERATURE,
        help="Temperature for Gen AI",
        type=_validate_temperature,
        metavar=str(DEFAULT_TEMPERATURE),
    )
    parser.add_argument(
        "--top-p",
        required=False,
        default=DEFAULT_TOP_P,
        help="Top P for Gen AI",
        type=_validate_top_p,
        metavar=str(DEFAULT_TOP_P),
    )
    args = parser.parse_args()

    run(
        args.room_code.upper(),
        args.chat_model_provider,
        chat_model_name=args.chat_model_name,
        num_of_bots=args.num_of_bots,
        bots_in_play=args.bots_in_play,
        chat_model_temperature=args.temperature,
        chat_model_top_p=args.top_p,
    )


if __name__ == "__main__":
    main()
