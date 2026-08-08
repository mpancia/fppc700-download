import json

import pytest
import requests

from fppc700download import fppc
from fppc700download.models import FilingType

FILER_LAST_NAME = "LAST"
FILER_FIRST_NAME = "FIRST"
FILER_AGENCY = "AGENCY"
FILER_POSITION = "POSITION"
FILING_YEAR = "YEAR"

DOCUMENT = {
    "filingInfo": {
        "noReportableInterests": False,
        "isAmendment": False,
        "filedDate": "2026-01-01T00:00:00",
    },
    "filer": {"lastName": 'Weird"}Name', "firstName": "FIRST"},
    "indexID": "FAKE-ID",
    "filingPositions": [
        {
            "agency": "AGENCY",
            "position": "POSITION",
            "filingType": "Annual",
            "filingYear": 2025,
        }
    ],
}


def test_make_download_payload():
    _EXPECTED = {
        "formInfo": {
            "LastName": "LAST",
            "FirstName": "FIRST",
            "Agency": "AGENCY",
            "Position": "POSITION",
            "FilingYear": 2025,
            "FilingType": "Annual",
        },
        "indexID": "FAKE-ID",
    }
    DOCUMENT_INDEX_ID = "FAKE-ID"
    actual = fppc._make_download_payload(
        FILER_LAST_NAME,
        FILER_FIRST_NAME,
        FILER_AGENCY,
        FILER_POSITION,
        2025,
        FilingType.ANNUAL,
        DOCUMENT_INDEX_ID,
    )
    assert actual == _EXPECTED


def test_make_search_payload():
    _EXPECTED = {
        "queryGenerationInfo": None,
        "searchFieldQueryInfos": [
            {"queryField": "FilerPosition", "filterValue": "POSITION"},
            {
                "queryField": "FilerFirstName",
                "queryType": "Start With",
                "filterValue": "FIRST",
            },
            {
                "queryField": "FilerLastName",
                "queryType": "Start With",
                "filterValue": "LAST",
            },
            {"queryField": "FilerAgency", "filterValue": "AGENCY"},
            {"queryField": "FilingType", "filterValue": []},
            {"queryField": "FilingYear", "filterValue": "YEAR"},
        ],
        "showOnlyHeldPositions": False,
    }
    actual = fppc._make_search_payload(
        FILER_FIRST_NAME,
        FILER_LAST_NAME,
        FILER_AGENCY,
        FILING_YEAR,
        FILER_POSITION,
        False,
        False,
    )
    assert actual == _EXPECTED


def test_make_search_payload_currently_held_positions():
    _EXPECTED = {
        "queryGenerationInfo": None,
        "searchFieldQueryInfos": [
            {"queryField": "FilerPosition", "filterValue": "POSITION"},
            {
                "queryField": "FilerFirstName",
                "queryType": "Start With",
                "filterValue": "FIRST",
            },
            {
                "queryField": "FilerLastName",
                "queryType": "Start With",
                "filterValue": "LAST",
            },
            {"queryField": "FilerAgency", "filterValue": "AGENCY"},
            {"queryField": "FilingType", "filterValue": []},
            {"queryField": "FilingYear", "filterValue": "YEAR"},
        ],
        "showOnlyHeldPositions": True,
    }
    actual = fppc._make_search_payload(
        FILER_FIRST_NAME,
        FILER_LAST_NAME,
        FILER_AGENCY,
        FILING_YEAR,
        FILER_POSITION,
        True,
        False,
    )
    assert actual == _EXPECTED


def test_make_search_payload_amendments_only():
    _EXPECTED = {
        "queryGenerationInfo": None,
        "searchFieldQueryInfos": [
            {"queryField": "FilerPosition", "filterValue": "POSITION"},
            {
                "queryField": "FilerFirstName",
                "queryType": "Start With",
                "filterValue": "FIRST",
            },
            {
                "queryField": "FilerLastName",
                "queryType": "Start With",
                "filterValue": "LAST",
            },
            {"queryField": "FilerAgency", "filterValue": "AGENCY"},
            {"queryField": "FilingType", "filterValue": []},
            {"queryField": "FilingYear", "filterValue": "YEAR"},
            {"queryField": "Amendment", "filterValue": "true"},
        ],
        "showOnlyHeldPositions": False,
    }
    actual = fppc._make_search_payload(
        FILER_FIRST_NAME,
        FILER_LAST_NAME,
        FILER_AGENCY,
        FILING_YEAR,
        FILER_POSITION,
        False,
        True,
    )
    assert actual == _EXPECTED


def test_search_for_documents_parses_nested_quotes(monkeypatch):
    body = json.dumps(json.dumps({"total": 1, "documents": [DOCUMENT]}))

    class FakeResponse:
        text = body

        def raise_for_status(self):
            pass

    monkeypatch.setattr(fppc._session, "post", lambda *args, **kwargs: FakeResponse())

    result = fppc.search_for_documents(
        FILER_FIRST_NAME,
        FILER_LAST_NAME,
        FILER_AGENCY,
        FILING_YEAR,
        FILER_POSITION,
        False,
        False,
    )

    assert result.total == 1
    assert result.documents[0].filer.last_name == 'Weird"}Name'
    assert result.documents[0].filing_positions[0].filing_type == FilingType.ANNUAL


def test_search_for_documents_raises_for_http_error(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            raise requests.HTTPError("500 Server Error")

    monkeypatch.setattr(fppc._session, "post", lambda *args, **kwargs: FakeResponse())

    with pytest.raises(requests.HTTPError):
        fppc.search_for_documents(
            FILER_FIRST_NAME,
            FILER_LAST_NAME,
            FILER_AGENCY,
            FILING_YEAR,
            FILER_POSITION,
            False,
            False,
        )
