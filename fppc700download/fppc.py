from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from .models import FilingType, SearchResult

SEARCH_URL = "https://form700search.fppc.ca.gov/Home/SearchDocuments"
DOWNLOAD_URL = "https://form700search.fppc.ca.gov/Home/GetRedactedFormPdf"

_session = requests.Session()


def _post_and_decode(url: str, payload: dict[str, Any]) -> Any:
    response = _session.post(
        url, headers={"content-type": "application/json"}, data=json.dumps(payload)
    )
    response.raise_for_status()
    return json.loads(json.loads(response.text))


def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = _post_and_decode(url, payload)
    assert isinstance(result, dict)
    return result


def autocomplete(field: str, prefix: str) -> list[str]:
    payload = {
        "isAutocompleteQuery": True,
        "searchFieldQueryInfos": [
            {
                "queryField": field,
                "queryType": "Start Match",
                "filterValue": prefix,
                "isAutoCompletePrimary": True,
            }
        ],
    }
    result = _post_and_decode(SEARCH_URL, payload)
    assert isinstance(result, list)
    return result


def _make_download_payload(
    filer_last_name: str,
    filer_first_name: str,
    filer_agency: str,
    filer_position: str,
    filing_year: int,
    filing_type: FilingType,
    document_index_id: str,
) -> dict[str, Any]:
    return {
        "formInfo": {
            "LastName": filer_last_name,
            "FirstName": filer_first_name,
            "Agency": filer_agency,
            "Position": filer_position,
            "FilingYear": filing_year,
            "FilingType": filing_type,
        },
        "indexID": document_index_id,
    }


def fetch_document_pdf(
    filer_last_name: str,
    filer_first_name: str,
    filer_agency: str,
    filer_position: str,
    filing_type: FilingType,
    filing_year: int,
    document_index_id: str,
) -> tuple[str, bytes]:
    payload = _make_download_payload(
        filer_last_name,
        filer_first_name,
        filer_agency,
        filer_position,
        filing_year,
        filing_type,
        document_index_id,
    )

    file_url_response = _session.post(
        DOWNLOAD_URL,
        headers={"content-type": "application/json"},
        data=json.dumps(payload),
    )
    file_url_response.raise_for_status()
    document_url: str = file_url_response.json()["PDFDownloadUrl"]

    file_response = _session.get(document_url)
    file_response.raise_for_status()

    return document_url, file_response.content


def download_document(
    filer_last_name: str,
    filer_first_name: str,
    filer_agency: str,
    filer_position: str,
    filing_type: FilingType,
    filing_year: int,
    document_index_id: str,
    output_directory: Path,
    file_name: str,
) -> str:
    document_url, content = fetch_document_pdf(
        filer_last_name,
        filer_first_name,
        filer_agency,
        filer_position,
        filing_type,
        filing_year,
        document_index_id,
    )
    (output_directory / file_name).write_bytes(content)
    return document_url


def _make_search_payload(
    filer_first_name: str,
    filer_last_name: str,
    filer_agency: str,
    filing_year: str,
    filer_position: str,
    currently_held_positions_only: bool,
    amendments_only: bool,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "queryGenerationInfo": None,
        "searchFieldQueryInfos": [],
        "showOnlyHeldPositions": currently_held_positions_only,
    }

    if filer_position != "":
        payload["searchFieldQueryInfos"].append(
            {"queryField": "FilerPosition", "filterValue": filer_position},
        )

    if filer_first_name != "":
        payload["searchFieldQueryInfos"].append(
            {
                "queryField": "FilerFirstName",
                "queryType": "Start With",
                "filterValue": filer_first_name,
            }
        )

    if filer_last_name != "":
        payload["searchFieldQueryInfos"].append(
            {
                "queryField": "FilerLastName",
                "queryType": "Start With",
                "filterValue": filer_last_name,
            }
        )

    if filer_agency != "":
        payload["searchFieldQueryInfos"].append(
            {
                "queryField": "FilerAgency",
                "filterValue": filer_agency,
            }
        )

    payload["searchFieldQueryInfos"].append(
        {"queryField": "FilingType", "filterValue": []}
    )

    if filing_year != "":
        payload["searchFieldQueryInfos"].append(
            {"queryField": "FilingYear", "filterValue": filing_year}
        )

    if amendments_only:
        payload["searchFieldQueryInfos"].append(
            {"queryField": "Amendment", "filterValue": "true"}
        )
    return payload


def search_for_documents(
    filer_first_name: str,
    filer_last_name: str,
    filer_agency: str,
    filing_year: str,
    filer_position: str,
    currently_held_positions_only: bool,
    amendments_only: bool,
) -> SearchResult:
    payload = _make_search_payload(
        filer_first_name,
        filer_last_name,
        filer_agency,
        filing_year,
        filer_position,
        currently_held_positions_only,
        amendments_only,
    )
    return SearchResult.from_api(_post_json(SEARCH_URL, payload))
