from nicegui import ui

from ai_plays_jackbox.ui.create_ui import create_ui


def web_ui(reload: bool = False):
    create_ui()
    ui.run(reload=reload)


if __name__ in {"__main__", "__mp_main__"}:
    web_ui(True)
