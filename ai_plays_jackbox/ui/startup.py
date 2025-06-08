from multiprocessing import Process, Queue

import psutil
from loguru import logger
from nicegui import app, ui

from ai_plays_jackbox.bot.bot_personality import JackBoxBotVariant
from ai_plays_jackbox.constants import (
    DEFAULT_NUM_OF_BOTS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
)
from ai_plays_jackbox.llm.chat_model_factory import CHAT_MODEL_PROVIDERS
from ai_plays_jackbox.run import run

LOG_QUEUE: Queue = Queue()
LOG_DISPLAY = None
SELECT_ALL_BOT_VARIANTS = None
BOT_VARIANT_CHECKBOX_STATES: dict = {}


def _format_log(record):
    thread_name = record["thread"].name
    color = "red"
    colored_name = f"<{color}>{thread_name:<12}</{color}>"

    return (
        f"<green>{record['time']:YYYY-MM-DD HH:mm:ss}</green> | "
        f"<cyan>{record['level']:<8}</cyan> | "
        f"{colored_name} | "
        f"{record['message']}\n"
    )


def _build_log_display():
    global LOG_DISPLAY
    with ui.row().classes("w-full"):
        LOG_DISPLAY = ui.log(max_lines=100).classes("h-64 overflow-auto bg-black text-white")
    ui.timer(interval=0.5, callback=_poll_log_queue)


def _poll_log_queue():
    global LOG_DISPLAY
    try:
        while not LOG_QUEUE.empty():
            log_msg = LOG_QUEUE.get_nowait()
            LOG_DISPLAY.push(log_msg)
    except Exception as e:
        LOG_DISPLAY.push(f"[ERROR] Failed to read log: {e}")


def _start(
    room_code: str,
    chat_model_provider: str,
    chat_model_name: str,
    num_of_bots: int,
    bots_in_play: list[str],
    temperature: float,
    top_p: float,
    log_queue: Queue,
):
    logger.add(lambda msg: log_queue.put(msg), format=_format_log)

    try:
        run(
            room_code.strip().upper(),
            chat_model_provider,
            chat_model_name=chat_model_name,
            num_of_bots=num_of_bots,
            bots_in_play=bots_in_play,
            chat_model_temperature=temperature,
            chat_model_top_p=top_p,
        )
    except Exception as e:
        logger.exception("Bot startup failed")


def _is_game_process_alive():
    game_pid = app.storage.general.get("game_pid", None)
    is_game_alive = game_pid is not None and psutil.pid_exists(game_pid) and psutil.Process(game_pid).is_running()
    if not is_game_alive:
        app.storage.general["game_pid"] = None
    return is_game_alive


def _handle_start_click(
    room_code: str,
    chat_model_provider: str,
    chat_model_name: str,
    num_of_bots: int,
    temperature: float,
    top_p: float,
):
    global BOT_VARIANT_CHECKBOX_STATES

    if not _is_game_process_alive():
        logger.info("Starting...")
        game_thread = Process(
            target=_start,
            args=(
                room_code,
                chat_model_provider,
                chat_model_name,
                num_of_bots,
                [k for k, v in BOT_VARIANT_CHECKBOX_STATES.items() if v.value],
                temperature,
                top_p,
                LOG_QUEUE,
            ),
            daemon=True,
        )
        game_thread.start()
        app.storage.general["game_pid"] = game_thread.pid


def _select_all_bot_variants_changed():
    for checkbox in BOT_VARIANT_CHECKBOX_STATES.values():
        checkbox.value = SELECT_ALL_BOT_VARIANTS.value


def _sync_select_all_bot_variants():
    all_checked = all(cb.value for cb in BOT_VARIANT_CHECKBOX_STATES.values())
    SELECT_ALL_BOT_VARIANTS.value = all_checked


def _setup_bot_variant_display():
    global SELECT_ALL_BOT_VARIANTS
    with ui.list().props("bordered separator").classes("w-full"):
        with ui.item_label("Bot Personalities").props("header").classes("text-bold"):
            SELECT_ALL_BOT_VARIANTS = ui.checkbox(text="Select All", value=True)
            SELECT_ALL_BOT_VARIANTS.on("update:model-value", lambda e: _select_all_bot_variants_changed())
        ui.separator()
        with ui.element("div").classes("overflow-y-auto h-64"):
            for variant in list(JackBoxBotVariant):
                with ui.item():
                    with ui.item_section().props("avatar"):
                        cb = ui.checkbox(value=True)
                        cb.on("update:model-value", lambda e: _sync_select_all_bot_variants())
                        BOT_VARIANT_CHECKBOX_STATES[variant.name] = cb
                    with ui.item_section():
                        ui.item_label(variant.value.name)
                        ui.item_label(variant.value.personality).props("caption")


def startup():
    ui.page_title("AI Plays JackBox")
    ui.label("🤖 AI Plays JackBox").classes("text-2xl font-bold")

    _build_log_display()

    with ui.grid(columns=16).classes("w-full gap-0"):
        with ui.column().classes("col-span-1"):
            pass
        with ui.column().classes("col-span-7"):
            with ui.row():
                ui.label("Number of Bots")
                num_of_bots_label = ui.label(str(DEFAULT_NUM_OF_BOTS))
                num_of_bots = ui.slider(
                    min=1,
                    max=10,
                    value=DEFAULT_NUM_OF_BOTS,
                    step=1,
                    on_change=lambda e: num_of_bots_label.set_text(f"{e.value}"),
                )
                chat_model_provider = ui.select(
                    list(CHAT_MODEL_PROVIDERS.keys()),
                    label="Chat Model Provider",
                    value=list(CHAT_MODEL_PROVIDERS.keys())[0],
                    on_change=lambda e: chat_model_name.set_value(CHAT_MODEL_PROVIDERS[e.value].get_default_model()),
                ).classes("w-1/3")

                chat_model_name = ui.input(
                    label="Chat Model Name",
                    value=CHAT_MODEL_PROVIDERS[chat_model_provider.value].get_default_model(),
                ).classes("w-1/3")

                room_code = (
                    ui.input(
                        label="Room Code",
                        placeholder="ABCD",
                        validation={
                            "must be letters only": lambda value: value.isalpha(),
                            "must be 4 letters": lambda value: len(value) == 4,
                        },
                    )
                    .props("uppercase")
                    .classes("w-1/4")
                )
                start_button = (
                    ui.button(
                        "Start Bots",
                        on_click=lambda _: _handle_start_click(
                            room_code.value,
                            chat_model_provider.value,
                            chat_model_name.value,
                            num_of_bots.value,
                            temperature.value,
                            top_p.value,
                        ),
                    )
                    .bind_enabled_from(room_code, "error", lambda error: room_code.value and not error)
                    .classes("w-full")
                )
                ui.timer(
                    interval=0.5,
                    callback=lambda: start_button.props(
                        f"color={'blue' if _is_game_process_alive() else 'green'}"
                    ).set_text("Running..." if _is_game_process_alive() else "Start Bots"),
                )

                ui.label("Advanced Options").classes("w-full text-xl font-bold")

                ui.label("Temperature").classes("w-1/4").tooltip(
                    """
                    What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
                    make the output more random, while lower values like 0.2 will make it more
                    focused and deterministic. We generally recommend altering this or `top_p` but
                    not both."""
                )
                temperature_label = ui.label(str(DEFAULT_TEMPERATURE)).classes("w-1/6")
                temperature = ui.slider(
                    min=0.0,
                    max=2.0,
                    value=DEFAULT_TEMPERATURE,
                    step=0.1,
                    on_change=lambda e: temperature_label.set_text(f"{e.value}"),
                ).classes("w-1/2")

                ui.label("Top P").classes("w-1/4").tooltip(
                    """
                    An alternative to sampling with temperature, called nucleus sampling, where the
                    model considers the results of the tokens with top_p probability mass. So 0.1
                    means only the tokens comprising the top 10% probability mass are considered."""
                )
                top_p_label = ui.label(str(DEFAULT_TOP_P)).classes("w-1/6")
                top_p = ui.slider(
                    min=0.0,
                    max=1.0,
                    value=DEFAULT_TOP_P,
                    step=0.1,
                    on_change=lambda e: top_p_label.set_text(f"{e.value}"),
                ).classes("w-1/2")

        with ui.column().classes("col-span-1"):
            pass

        with ui.column().classes("col-span-6"):
            _setup_bot_variant_display()
