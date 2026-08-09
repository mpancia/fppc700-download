from click.testing import CliRunner

import fppc700download.cli as cli
from fppc700download.models import SearchResult


def _document(position, index_id="FAKE-ID"):
    return {
        "filer": {"lastName": "LAST", "firstName": "FIRST"},
        "filingPositions": [
            {
                "agency": "AGENCY",
                "position": position,
                "filingType": "Annual",
                "filingYear": 2026,
            }
        ],
        "filingInfo": {
            "filedDate": "2026-01-01T00:00:00",
            "isAmendment": False,
            "noReportableInterests": False,
        },
        "indexID": index_id,
    }


def _document_with_positions(positions, index_id="FAKE-ID"):
    return {
        "filer": {"lastName": "LAST", "firstName": "FIRST"},
        "filingPositions": [
            {
                "agency": "AGENCY",
                "position": position,
                "filingType": "Annual",
                "filingYear": 2026,
            }
            for position in positions
        ],
        "filingInfo": {
            "filedDate": "2026-01-01T00:00:00",
            "isAmendment": False,
            "noReportableInterests": False,
        },
        "indexID": index_id,
    }


def test_creates_output_directory_if_missing(tmp_path, monkeypatch):
    output_directory = tmp_path / "reports"

    result_data = SearchResult.from_api(
        {"total": 1, "documents": [_document("POSITION")]}
    )
    monkeypatch.setattr(
        cli, "search_for_documents", lambda *args, **kwargs: result_data
    )
    monkeypatch.setattr(cli, "download_document", lambda *args, **kwargs: None)

    runner = CliRunner()
    result = runner.invoke(
        cli.search,
        ["--output-directory", str(output_directory)],
    )

    assert result.exit_code == 0
    assert output_directory.is_dir()


def test_filters_out_documents_with_a_different_position(tmp_path, monkeypatch):
    result_data = SearchResult.from_api(
        {
            "total": 2,
            "documents": [
                _document("Judge", "MATCH"),
                _document("Retired Judge", "SKIP"),
            ],
        }
    )
    monkeypatch.setattr(
        cli, "search_for_documents", lambda *args, **kwargs: result_data
    )

    downloaded = []
    monkeypatch.setattr(
        cli, "download_document", lambda *args: downloaded.append(args[6])
    )

    runner = CliRunner()
    result = runner.invoke(
        cli.search,
        ["--filer-position", "Judge", "--output-directory", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert downloaded == ["MATCH"]


def test_matches_position_anywhere_in_filing_positions(tmp_path, monkeypatch):
    result_data = SearchResult.from_api(
        {
            "total": 1,
            "documents": [
                _document_with_positions(
                    ["Board Member", "Supervisor", "Alternate Board Member"], "MATCH"
                )
            ],
        }
    )
    monkeypatch.setattr(
        cli, "search_for_documents", lambda *args, **kwargs: result_data
    )

    downloaded = []
    monkeypatch.setattr(
        cli, "download_document", lambda *args: downloaded.append(args[3])
    )

    runner = CliRunner()
    result = runner.invoke(
        cli.search,
        ["--filer-position", "Supervisor", "--output-directory", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert downloaded == ["Supervisor"]


def test_cli_defaults_to_search_without_a_subcommand(tmp_path, monkeypatch, caplog):
    caplog.set_level("INFO")
    result_data = SearchResult.from_api({"total": 0, "documents": []})
    monkeypatch.setattr(
        cli, "search_for_documents", lambda *args, **kwargs: result_data
    )

    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        ["--filer-last-name", "K", "--output-directory", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "No documents found" in caplog.text
