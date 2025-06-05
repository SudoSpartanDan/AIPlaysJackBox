import threading
from collections import deque

from loguru import logger
from nicegui import ui

from ai_plays_jackbox import run
from ai_plays_jackbox.bot.bot_personality import JackBoxBotVariant


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


# Keep a reference to the game thread
game_thread = None


def create_ui():
    def _handle_start_click():
        global game_thread

        def _start_in_thread():
            bots_in_play = [k for k, v in bot_variant_checkbox_states.items() if v.value]
            try:
                run(
                    room_code.value.strip().upper(),
                    num_of_bots=num_of_bots.value,
                    bots_in_play=bots_in_play,
                    chat_model_name=chat_model.value,
                    chat_model_temperature=temperature.value,
                    chat_model_top_p=top_p.value,
                )
            except Exception as e:
                logger.exception("Bot startup failed")

        game_thread = threading.Thread(target=_start_in_thread, daemon=True)
        game_thread.start()
        start_button.disable()
        start_button.props("color=blue")
        start_button.text = "Running..."

    def _refresh_button_state():
        if game_thread and not game_thread.is_alive():
            start_button.enable()
            start_button.props("color=green")
            start_button.text = "Start Bots"

    ui.label("🤖 AI Plays JackBox").classes("text-2xl font-bold")

    with ui.row().classes("w-full"):

        log_display = ui.log(max_lines=100).classes("h-64 overflow-auto bg-black text-white")
        log_buffer = deque(maxlen=100)

        def _ui_log_sink(message):
            log_buffer.append(message)
            log_display.push(message.strip())

        logger.add(_ui_log_sink, format=_format_log, level="INFO", enqueue=True)

    with ui.grid(columns=16).classes("w-full gap-0"):
        with ui.column().classes("col-span-1"):
            pass
        with ui.column().classes("col-span-7"):
            with ui.row():
                ui.label("Number of Bots")
                num_of_bots_label = ui.label("4")
                num_of_bots = ui.slider(
                    min=1,
                    max=10,
                    value=4,
                    step=1,
                    on_change=lambda e: num_of_bots_label.set_text(f"{e.value}"),
                )
                chat_model = ui.select(["ollama", "openai", "gemini"], label="Chat Model", value="ollama").classes(
                    "w-1/3"
                )
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
                    ui.button("Start Bots", on_click=_handle_start_click, color="green")
                    .bind_enabled_from(room_code, "error", lambda error: room_code.value and not error)
                    .classes("w-1/3")
                )

                ui.label("Advanced Options").classes("w-full text-xl font-bold")

                ui.label("Temperature").classes("w-1/4").tooltip(
                    """
                    What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
                    make the output more random, while lower values like 0.2 will make it more
                    focused and deterministic. We generally recommend altering this or `top_p` but
                    not both."""
                )
                temperature_label = ui.label("0.5").classes("w-1/6")
                temperature = ui.slider(
                    min=0.0,
                    max=2.0,
                    value=0.5,
                    step=0.1,
                    on_change=lambda e: temperature_label.set_text(f"{e.value}"),
                ).classes("w-1/2")

                ui.label("Top P").classes("w-1/4").tooltip(
                    """
                    An alternative to sampling with temperature, called nucleus sampling, where the
                    model considers the results of the tokens with top_p probability mass. So 0.1
                    means only the tokens comprising the top 10% probability mass are considered."""
                )
                top_p_label = ui.label("0.9").classes("w-1/6")
                top_p = ui.slider(
                    min=0.0,
                    max=1.0,
                    value=0.9,
                    step=0.1,
                    on_change=lambda e: top_p_label.set_text(f"{e.value}"),
                ).classes("w-1/2")

        with ui.column().classes("col-span-1"):
            pass

        bot_variant_checkbox_states = {}

        def select_all_changed():
            for checkbox in bot_variant_checkbox_states.values():
                checkbox.value = select_all_bot_variants.value

        def sync_select_all():
            all_checked = all(cb.value for cb in bot_variant_checkbox_states.values())
            select_all_bot_variants.value = all_checked

        with ui.column().classes("col-span-6"):
            with ui.list().props("bordered separator").classes("w-full"):
                with ui.item_label("Bot Personalities").props("header").classes("text-bold"):
                    select_all_bot_variants = ui.checkbox(text="Select All", value=True)
                    select_all_bot_variants.on("update:model-value", lambda e: select_all_changed())
                ui.separator()
                with ui.element("div").classes("overflow-y-auto h-64"):
                    for variant in list(JackBoxBotVariant):
                        with ui.item():
                            with ui.item_section().props("avatar"):
                                cb = ui.checkbox(value=True)
                                cb.on("update:model-value", lambda e: sync_select_all())
                                bot_variant_checkbox_states[variant.name] = cb
                            with ui.item_section():
                                ui.item_label(variant.value.name)
                                ui.item_label(variant.value.personality).props("caption")

    ui.timer(1.0, _refresh_button_state)
