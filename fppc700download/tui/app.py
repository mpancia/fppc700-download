import asyncio
from collections.abc import Iterable
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import Screen
from textual.suggester import Suggester
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    RichLog,
)
from textual.worker import Worker, WorkerState

from ..format import format_pdf_file_name
from ..fppc import autocomplete, download_document, search_for_documents
from ..models import (
    Document,
    FilingPosition,
    SearchResult,
    matching_filing_positions,
)


class FppcFieldSuggester(Suggester):
    def __init__(self, field: str) -> None:
        super().__init__(case_sensitive=False)
        self._field = field

    async def get_suggestion(self, value: str) -> str | None:
        if not value:
            return None
        loop = asyncio.get_running_loop()
        try:
            matches = await loop.run_in_executor(None, autocomplete, self._field, value)
        except Exception:
            return None
        for match in matches:
            if match.casefold().startswith(value.casefold()):
                return match
        return None


_AGENCY_SUGGESTER = FppcFieldSuggester("FilerAgency")
_POSITION_SUGGESTER = FppcFieldSuggester("FilerPosition")


RESULTS_COLUMNS = (
    ("Last", "last"),
    ("First", "first"),
    ("Agency", "agency"),
    ("Position", "position"),
    ("Type", "type"),
    ("Year", "year"),
    ("Filed", "filed"),
    ("Amendment", "amendment"),
)


class DownloadProgress(Message):
    def __init__(self, completed: int, total: int, label: str) -> None:
        self.completed = completed
        self.total = total
        self.label = label
        super().__init__()


class DownloadFileError(Message):
    def __init__(self, label: str, error: str) -> None:
        self.label = label
        self.error = error
        super().__init__()


class FppcApp(App[None]):
    TITLE = "FPPC Form 700 Downloader"
    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("ctrl+s", "search", "Search"),
        ("ctrl+d", "download_all", "Download all"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._rows: dict[str, tuple[Document, FilingPosition]] = {}
        self._sort_column: str | None = None
        self._sort_reverse: bool = False

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
                yield Input(
                    placeholder="Agency to search",
                    id="filer-agency",
                    suggester=_AGENCY_SUGGESTER,
                )
            with Vertical(classes="field"):
                yield Label("Position")
                yield Input(
                    placeholder='e.g. "Assembly Member"',
                    id="filer-position",
                    suggester=_POSITION_SUGGESTER,
                )
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
            yield DataTable(id="results-table", cursor_type="row")
            yield Button("Download all", id="download-all-button")
            yield ProgressBar(id="download-progress", show_eta=False)
            yield RichLog(id="download-log", wrap=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).add_columns(*RESULTS_COLUMNS)

    @on(DataTable.HeaderSelected)
    def handle_header_selected(self, event: DataTable.HeaderSelected) -> None:
        column_key = event.column_key.value
        if column_key is None:
            return
        self._sort_reverse = (
            not self._sort_reverse if column_key == self._sort_column else False
        )
        self._sort_column = column_key
        self.query_one(DataTable).sort(event.column_key, reverse=self._sort_reverse)

    def get_system_commands(self, screen: Screen[object]) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("Search", "Run a search", self.action_search)
        yield SystemCommand(
            "Download all", "Download every result", self.action_download_all
        )

    @on(Button.Pressed, "#search-button")
    def handle_search_pressed(self) -> None:
        self.action_search()

    def action_search(self) -> None:
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
            self._populate_results(
                event.worker.result,
                self.query_one("#filer-agency", Input).value,
                self.query_one("#filer-position", Input).value,
            )
        elif event.state == WorkerState.ERROR:
            self.query_one("#status-message", Label).update(
                f"Error: {event.worker.error}"
            )

    def _populate_results(
        self, result: SearchResult, filer_agency: str, filer_position: str
    ) -> None:
        table = self.query_one(DataTable)
        table.clear()
        self._rows.clear()

        for document in result.documents:
            positions = matching_filing_positions(
                document, filer_agency, filer_position
            )
            for index, position in enumerate(positions):
                key = f"{document.index_id}:{index}"
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

    @on(DataTable.RowSelected)
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        entry = self._rows.get(event.row_key.value or "")
        if entry is not None:
            self._start_download([entry])

    @on(Button.Pressed, "#download-all-button")
    def handle_download_all_pressed(self) -> None:
        self.action_download_all()

    def action_download_all(self) -> None:
        self._start_download(list(self._rows.values()))

    def _start_download(self, entries: list[tuple[Document, FilingPosition]]) -> None:
        if not entries:
            return
        output_directory = Path(self.query_one("#output-directory", Input).value)
        ignore_existing = self.query_one("#ignore-existing-files", Checkbox).value
        self.query_one(ProgressBar).update(total=len(entries), progress=0)
        self.run_downloads(entries, output_directory, ignore_existing)

    @work(thread=True, exclusive=True, group="download")
    def run_downloads(
        self,
        entries: list[tuple[Document, FilingPosition]],
        output_directory: Path,
        ignore_existing: bool,
    ) -> None:
        output_directory.mkdir(parents=True, exist_ok=True)
        existing_files = {path.name for path in output_directory.iterdir()}
        total = len(entries)

        for completed, (document, position) in enumerate(entries, start=1):
            label = f"{document.filer.last_name}, {document.filer.first_name} ({position.position})"
            file_name = format_pdf_file_name(document, position)

            if ignore_existing and file_name in existing_files:
                self.post_message(
                    DownloadProgress(completed, total, f"{label} — already exists")
                )
                continue

            try:
                download_document(
                    document.filer.last_name,
                    document.filer.first_name,
                    position.agency,
                    position.position,
                    position.filing_type,
                    position.filing_year,
                    document.index_id,
                    output_directory,
                    file_name,
                )
            except Exception as error:
                self.post_message(DownloadFileError(label, str(error)))
            else:
                self.post_message(DownloadProgress(completed, total, label))

    @on(DownloadProgress)
    def handle_download_progress(self, event: DownloadProgress) -> None:
        self.query_one(ProgressBar).update(progress=event.completed)
        self.query_one(RichLog).write(
            f"[{event.completed}/{event.total}] {event.label}"
        )

    @on(DownloadFileError)
    def handle_download_file_error(self, event: DownloadFileError) -> None:
        self.query_one(RichLog).write(f"FAILED: {event.label} — {event.error}")


def run() -> None:
    FppcApp().run()
