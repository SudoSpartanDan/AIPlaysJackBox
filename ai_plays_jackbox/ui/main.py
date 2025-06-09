from nicegui import app, ui

from ai_plays_jackbox.ui.startup import startup


def main(reload: bool = False):
    app.on_startup(startup)
    ui.run(favicon="🤖", reload=reload)


if __name__ in {"__main__", "__mp_main__"}:
    main(True)
