from click.testing import CliRunner

import fppc700download.cli as cli


def _document(position, index_id="FAKE-ID"):
    return {
        "filer": {"lastName": "LAST", "firstName": "FIRST"},
        "filingPositions": [
            {
                "agency": "AGENCY",
                "position": position,
                "filingType": "TYPE",
                "filingYear": "YEAR",
            }
        ],
        "filingInfo": {"filedDate": "2026-01-01T00:00:00"},
        "indexID": index_id,
    }


def test_creates_output_directory_if_missing(tmp_path, monkeypatch):
    output_directory = tmp_path / "reports"

    monkeypatch.setattr(
        cli,
        "search_for_documents",
        lambda *args, **kwargs: {"total": 1, "documents": [_document("POSITION")]},
    )
    monkeypatch.setattr(cli, "download_document", lambda *args, **kwargs: None)

    runner = CliRunner()
    result = runner.invoke(
        cli.search_and_download_documents,
        ["--output-directory", str(output_directory)],
    )

    assert result.exit_code == 0
    assert output_directory.is_dir()


def test_filters_out_documents_with_a_different_position(tmp_path, monkeypatch):
    documents = {
        "total": 2,
        "documents": [
            _document("Judge", "MATCH"),
            _document("Retired Judge", "SKIP"),
        ],
    }
    monkeypatch.setattr(cli, "search_for_documents", lambda *args, **kwargs: documents)

    downloaded = []
    monkeypatch.setattr(
        cli, "download_document", lambda *args: downloaded.append(args[6])
    )

    runner = CliRunner()
    result = runner.invoke(
        cli.search_and_download_documents,
        ["--filer-position", "Judge", "--output-directory", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert downloaded == ["MATCH"]
