from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class FppcApp(App[None]):
    TITLE = "FPPC Form 700 Downloader"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()


def run() -> None:
    FppcApp().run()
