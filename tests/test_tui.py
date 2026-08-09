from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    ProgressBar,
    RichLog,
)
from textual_autocomplete import TargetState

import fppc700download.tui.app as tui_app
from fppc700download.models import SearchResult
from fppc700download.tui.app import FppcApp

SAMPLE_RESULTS = {
    "total": 1,
    "documents": [
        {
            "filer": {"lastName": "LAST", "firstName": "FIRST"},
            "filingPositions": [
                {
                    "agency": "AGENCY",
                    "position": "POSITION",
                    "filingType": "Annual",
                    "filingYear": 2025,
                }
            ],
            "filingInfo": {
                "filedDate": "2026-01-01T00:00:00",
                "isAmendment": False,
                "noReportableInterests": False,
            },
            "indexID": "FAKE-ID",
        }
    ],
}


def _mock_search(monkeypatch, results=SAMPLE_RESULTS):
    monkeypatch.setattr(
        tui_app,
        "search_for_documents",
        lambda *args, **kwargs: SearchResult.from_api(results),
    )


async def test_app_mounts_header_and_footer():
    app = FppcApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one(Header) is not None
        assert app.query_one(Footer) is not None


async def test_search_form_has_all_expected_fields():
    app = FppcApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        for field_id in (
            "filer-first-name",
            "filer-last-name",
            "filer-agency",
            "filer-position",
            "filing-year",
            "output-directory",
        ):
            assert app.query_one(f"#{field_id}", Input) is not None

        for checkbox_id in (
            "amendments-only",
            "currently-held-positions-only",
            "ignore-existing-files",
        ):
            assert app.query_one(f"#{checkbox_id}", Checkbox) is not None

        assert app.query_one("#output-directory", Input).value == "."
        assert app.query_one("#search-button", Button) is not None


async def test_search_populates_results_table(monkeypatch):
    _mock_search(monkeypatch)

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        await pilot.click("#search-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        table = app.query_one(DataTable)
        assert table.row_count == 1
        assert app.query_one("#status-message").content == "1 document(s) found"


async def test_download_all_downloads_every_row(tmp_path, monkeypatch):
    _mock_search(monkeypatch)
    downloaded = []
    monkeypatch.setattr(
        tui_app, "download_document", lambda *args: downloaded.append(args[6])
    )

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        await pilot.click("#search-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        app.query_one("#output-directory", Input).value = str(tmp_path)
        await pilot.click("#download-all-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        assert downloaded == ["FAKE-ID"]
        assert app.query_one(ProgressBar).progress == 1
        assert len(app.query_one(RichLog).lines) == 1


async def test_ctrl_s_binding_triggers_search(monkeypatch):
    _mock_search(monkeypatch)

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        await pilot.press("ctrl+s")
        await app.workers.wait_for_complete()
        await pilot.pause()

        assert app.query_one(DataTable).row_count == 1


async def test_ctrl_d_binding_triggers_download_all(tmp_path, monkeypatch):
    _mock_search(monkeypatch)
    downloaded = []
    monkeypatch.setattr(
        tui_app, "download_document", lambda *args: downloaded.append(args[6])
    )

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        await pilot.click("#search-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        app.query_one("#output-directory", Input).value = str(tmp_path)
        await pilot.press("ctrl+d")
        await app.workers.wait_for_complete()
        await pilot.pause()

        assert downloaded == ["FAKE-ID"]


async def test_command_palette_includes_search_and_download_all():
    app = FppcApp()
    async with app.run_test() as pilot:
        commands = {command.title for command in app.get_system_commands(app.screen)}
        assert "Search" in commands
        assert "Download all" in commands
        await pilot.pause()


async def test_search_handles_duplicate_positions_within_a_document(monkeypatch):
    results = {
        "total": 1,
        "documents": [
            {
                "filer": {"lastName": "PESKIN", "firstName": "AARON"},
                "filingPositions": [
                    {
                        "agency": "City and County of San Francisco",
                        "position": "Supervisor",
                        "filingType": "Annual",
                        "filingYear": 2025,
                    },
                    {
                        "agency": "City and County of San Francisco",
                        "position": "Supervisor",
                        "filingType": "Annual",
                        "filingYear": 2025,
                    },
                ],
                "filingInfo": {
                    "filedDate": "2026-01-01T00:00:00",
                    "isAmendment": False,
                    "noReportableInterests": False,
                },
                "indexID": "FAKE-ID",
            }
        ],
    }
    _mock_search(monkeypatch, results)

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        await pilot.click("#search-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        assert app.query_one(DataTable).row_count == 2


async def test_search_filters_out_non_matching_positions(monkeypatch):
    results = {
        "total": 2,
        "documents": [
            {
                "filer": {"lastName": "MATCH", "firstName": "FIRST"},
                "filingPositions": [
                    {
                        "agency": "AGENCY",
                        "position": "Supervisor",
                        "filingType": "Annual",
                        "filingYear": 2025,
                    }
                ],
                "filingInfo": {
                    "filedDate": "2026-01-01T00:00:00",
                    "isAmendment": False,
                    "noReportableInterests": False,
                },
                "indexID": "MATCH-ID",
            },
            {
                "filer": {"lastName": "NOMATCH", "firstName": "FIRST"},
                "filingPositions": [
                    {
                        "agency": "AGENCY",
                        "position": "Bookstore Supervisor",
                        "filingType": "Annual",
                        "filingYear": 2025,
                    }
                ],
                "filingInfo": {
                    "filedDate": "2026-01-01T00:00:00",
                    "isAmendment": False,
                    "noReportableInterests": False,
                },
                "indexID": "NOMATCH-ID",
            },
        ],
    }
    _mock_search(monkeypatch, results)

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        app.query_one("#filer-position", Input).value = "Supervisor"
        await pilot.click("#search-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        table = app.query_one(DataTable)
        assert table.row_count == 1
        assert list(app._rows.values())[0][0].index_id == "MATCH-ID"


async def test_clicking_header_sorts_and_toggles_direction(monkeypatch):
    results = {
        "total": 3,
        "documents": [
            {
                "filer": {"lastName": name, "firstName": "FIRST"},
                "filingPositions": [
                    {
                        "agency": "AGENCY",
                        "position": "POSITION",
                        "filingType": "Annual",
                        "filingYear": 2025,
                    }
                ],
                "filingInfo": {
                    "filedDate": "2026-01-01T00:00:00",
                    "isAmendment": False,
                    "noReportableInterests": False,
                },
                "indexID": f"ID-{name}",
            }
            for name in ["Charlie", "Alpha", "Bravo"]
        ],
    }
    _mock_search(monkeypatch, results)

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        await pilot.click("#search-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        table = app.query_one(DataTable)
        assert [table.get_row_at(i)[1] for i in range(3)] == [
            "Charlie",
            "Alpha",
            "Bravo",
        ]

        await pilot.click(DataTable, offset=(7, 0))
        await pilot.pause()
        assert [table.get_row_at(i)[1] for i in range(3)] == [
            "Alpha",
            "Bravo",
            "Charlie",
        ]

        await pilot.click(DataTable, offset=(7, 0))
        await pilot.pause()
        assert [table.get_row_at(i)[1] for i in range(3)] == [
            "Charlie",
            "Bravo",
            "Alpha",
        ]


async def test_space_toggles_row_selection_and_updates_button_label(monkeypatch):
    results = {
        "total": 2,
        "documents": [
            {
                "filer": {"lastName": name, "firstName": "FIRST"},
                "filingPositions": [
                    {
                        "agency": "AGENCY",
                        "position": "POSITION",
                        "filingType": "Annual",
                        "filingYear": 2025,
                    }
                ],
                "filingInfo": {
                    "filedDate": "2026-01-01T00:00:00",
                    "isAmendment": False,
                    "noReportableInterests": False,
                },
                "indexID": f"ID-{name}",
            }
            for name in ["Alpha", "Bravo"]
        ],
    }
    _mock_search(monkeypatch, results)

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        await pilot.click("#search-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        button = app.query_one("#download-all-button", Button)
        table = app.query_one(DataTable)
        assert button.label == "Download all"

        await pilot.press("space")
        await pilot.pause()

        assert button.label == "Download selected (1)"
        assert table.get_row_at(0)[0] == "✓"

        await pilot.press("space")
        await pilot.pause()

        assert button.label == "Download all"
        assert table.get_row_at(0)[0] == ""


async def test_download_only_downloads_selected_rows(tmp_path, monkeypatch):
    results = {
        "total": 2,
        "documents": [
            {
                "filer": {"lastName": name, "firstName": "FIRST"},
                "filingPositions": [
                    {
                        "agency": "AGENCY",
                        "position": "POSITION",
                        "filingType": "Annual",
                        "filingYear": 2025,
                    }
                ],
                "filingInfo": {
                    "filedDate": "2026-01-01T00:00:00",
                    "isAmendment": False,
                    "noReportableInterests": False,
                },
                "indexID": f"ID-{name}",
            }
            for name in ["Alpha", "Bravo"]
        ],
    }
    _mock_search(monkeypatch, results)
    downloaded = []
    monkeypatch.setattr(
        tui_app, "download_document", lambda *args: downloaded.append(args[6])
    )

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        await pilot.click("#search-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        app.query_one("#output-directory", Input).value = str(tmp_path)

        await pilot.press("space")
        await pilot.pause()

        await pilot.click("#download-all-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        assert downloaded == ["ID-Alpha"]
        assert app.query_one("#download-all-button", Button).label == "Download all"


async def test_autocomplete_returns_empty_for_blank_text():
    app = FppcApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = next(
            w for w in app.query(tui_app.FppcAutoComplete) if w._field == "FilerAgency"
        )
        assert widget.get_candidates(TargetState(text="", cursor_position=0)) == []


async def test_autocomplete_fetches_then_serves_from_cache(monkeypatch):
    monkeypatch.setattr(
        tui_app,
        "autocomplete",
        lambda field, prefix: ["City and County of San Francisco", "City of Alameda"],
    )

    app = FppcApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = next(
            w for w in app.query(tui_app.FppcAutoComplete) if w._field == "FilerAgency"
        )
        state = TargetState(text="City", cursor_position=4)

        assert widget.get_candidates(state) == []

        await app.workers.wait_for_complete()
        await pilot.pause()

        assert [item.value for item in widget.get_candidates(state)] == [
            "City and County of San Francisco",
            "City of Alameda",
        ]


async def test_autocomplete_narrows_from_cached_superset(monkeypatch):
    monkeypatch.setattr(
        tui_app,
        "autocomplete",
        lambda field, prefix: ["City and County of San Francisco", "City of Alameda"],
    )

    app = FppcApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = next(
            w for w in app.query(tui_app.FppcAutoComplete) if w._field == "FilerAgency"
        )
        widget.get_candidates(TargetState(text="City", cursor_position=4))
        await app.workers.wait_for_complete()
        await pilot.pause()

        narrowed = widget.get_candidates(TargetState(text="City a", cursor_position=6))
        assert [item.value for item in narrowed] == ["City and County of San Francisco"]


async def test_autocomplete_handles_fetch_errors(monkeypatch):
    def raise_error(field, prefix):
        raise RuntimeError("boom")

    monkeypatch.setattr(tui_app, "autocomplete", raise_error)

    app = FppcApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = next(
            w for w in app.query(tui_app.FppcAutoComplete) if w._field == "FilerAgency"
        )
        state = TargetState(text="City", cursor_position=4)

        widget.get_candidates(state)
        await app.workers.wait_for_complete()
        await pilot.pause()

        assert widget.get_candidates(state) == []
