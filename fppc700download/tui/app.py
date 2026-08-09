from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
)
from textual.worker import Worker, WorkerState

from ..fppc import search_for_documents
from ..models import Document, FilingPosition, SearchResult

RESULTS_COLUMNS = (
    "Last",
    "First",
    "Agency",
    "Position",
    "Type",
    "Year",
    "Filed",
    "Amendment",
)


class FppcApp(App[None]):
    TITLE = "FPPC Form 700 Downloader"
    CSS_PATH = "app.tcss"

    def __init__(self) -> None:
        super().__init__()
        self._rows: dict[str, tuple[Document, FilingPosition]] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="search-form"):
            with Vertical(classes="field"):
                yield Label("First name")
                yield Input(placeholder="First name starts with", id="filer-first-name")
            with Vertical(classes="field"):
                yield Label("Last name")
                yield Input(placeholder="Last name starts with", id="filer-last-name")
            with Vertical(classes="field"):
                yield Label("Agency")
                yield Input(placeholder="Agency to search", id="filer-agency")
            with Vertical(classes="field"):
                yield Label("Position")
                yield Input(placeholder='e.g. "Assembly Member"', id="filer-position")
            with Vertical(classes="field"):
                yield Label("Filing year")
                yield Input(placeholder="e.g. 2025", id="filing-year")
            with Vertical(classes="field"):
                yield Label("Output directory")
                yield Input(value=".", id="output-directory")
            with Horizontal(id="search-flags"):
                yield Checkbox("Amendments only", id="amendments-only")
                yield Checkbox(
                    "Currently held positions only",
                    id="currently-held-positions-only",
                )
                yield Checkbox("Ignore existing files", id="ignore-existing-files")
            yield Button("Search", id="search-button", variant="primary")
            yield Label("", id="status-message")
            yield DataTable(id="results-table")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).add_columns(*RESULTS_COLUMNS)

    @on(Button.Pressed, "#search-button")
    def handle_search_pressed(self) -> None:
        self.query_one("#search-button", Button).disabled = True
        self.query_one("#status-message", Label).update("Searching…")
        self.run_search(
            self.query_one("#filer-first-name", Input).value,
            self.query_one("#filer-last-name", Input).value,
            self.query_one("#filer-agency", Input).value,
            self.query_one("#filing-year", Input).value,
            self.query_one("#filer-position", Input).value,
            self.query_one("#currently-held-positions-only", Checkbox).value,
            self.query_one("#amendments-only", Checkbox).value,
        )

    @work(thread=True, exclusive=True)
    def run_search(
        self,
        filer_first_name: str,
        filer_last_name: str,
        filer_agency: str,
        filing_year: str,
        filer_position: str,
        currently_held_positions_only: bool,
        amendments_only: bool,
    ) -> SearchResult:
        return search_for_documents(
            filer_first_name,
            filer_last_name,
            filer_agency,
            filing_year,
            filer_position,
            currently_held_positions_only,
            amendments_only,
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "run_search":
            return

        self.query_one("#search-button", Button).disabled = False

        if event.state == WorkerState.SUCCESS:
            assert event.worker.result is not None
            self._populate_results(event.worker.result)
        elif event.state == WorkerState.ERROR:
            self.query_one("#status-message", Label).update(
                f"Error: {event.worker.error}"
            )

    def _populate_results(self, result: SearchResult) -> None:
        table = self.query_one(DataTable)
        table.clear()
        self._rows.clear()

        for document in result.documents:
            for position in document.filing_positions:
                key = f"{document.index_id}:{position.agency}:{position.position}"
                self._rows[key] = (document, position)
                table.add_row(
                    document.filer.last_name,
                    document.filer.first_name,
                    position.agency,
                    position.position,
                    position.filing_type.value,
                    position.filing_year,
                    document.filing_info.filed_date[:10],
                    "Yes" if document.filing_info.is_amendment else "",
                    key=key,
                )

        self.query_one("#status-message", Label).update(
            f"{result.total} document(s) found"
        )


def run() -> None:
    FppcApp().run()
