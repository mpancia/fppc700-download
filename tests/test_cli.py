from click.testing import CliRunner

import fppc700download.cli as cli


def _fake_search_results():
    return {
        "total": 1,
        "documents": [
            {
                "filer": {"lastName": "LAST", "firstName": "FIRST"},
                "filingPositions": [
                    {
                        "agency": "AGENCY",
                        "position": "POSITION",
                        "filingType": "TYPE",
                        "filingYear": "YEAR",
                    }
                ],
                "filingInfo": {"filedDate": "2026-01-01T00:00:00"},
                "indexID": "FAKE-ID",
            }
        ],
    }


def test_creates_output_directory_if_missing(tmp_path, monkeypatch):
    output_directory = tmp_path / "reports"

    monkeypatch.setattr(
        cli, "search_for_documents", lambda *args, **kwargs: _fake_search_results()
    )
    monkeypatch.setattr(cli, "download_document", lambda *args, **kwargs: None)

    runner = CliRunner()
    result = runner.invoke(
        cli.search_and_download_documents,
        ["--output-directory", str(output_directory)],
    )

    assert result.exit_code == 0
    assert output_directory.is_dir()
