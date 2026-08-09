from textual.widgets import Button, Checkbox, DataTable, Footer, Header, Input

import fppc700download.tui.app as tui_app
from fppc700download.models import SearchResult
from fppc700download.tui.app import FppcApp


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
    documents = {
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
    monkeypatch.setattr(
        tui_app,
        "search_for_documents",
        lambda *args, **kwargs: SearchResult.from_api(documents),
    )

    app = FppcApp()
    async with app.run_test(size=(80, 50)) as pilot:
        await pilot.click("#search-button")
        await app.workers.wait_for_complete()
        await pilot.pause()

        table = app.query_one(DataTable)
        assert table.row_count == 1
        assert app.query_one("#status-message").content == "1 document(s) found"
