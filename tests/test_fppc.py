from fppc700download.fppc import _make_download_payload, _make_search_payload

FILER_LAST_NAME = "LAST"
FILER_FIRST_NAME = "FIRST"
FILER_AGENCY = "AGENCY"
FILER_POSITION = "POSITION"
FILING_TYPE = "TYPE"
FILING_YEAR = "YEAR"


def test_make_download_payload():
    _EXPECTED = {
        "formInfo": {
            "LastName": "LAST",
            "FirstName": "FIRST",
            "Agency": "AGENCY",
            "Position": "POSITION",
            "FilingYear": "YEAR",
            "FilingType": "TYPE",
        },
        "indexID": "FAKE-ID",
    }
    DOCUMENT_INDEX_ID = "FAKE-ID"
    actual = _make_download_payload(
        FILER_LAST_NAME,
        FILER_FIRST_NAME,
        FILER_AGENCY,
        FILER_POSITION,
        FILING_YEAR,
        FILING_TYPE,
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
            {"queryField": "FilingType", "filterValue": []},
            {"queryField": "FilingYear", "filterValue": "YEAR"},
        ],
        "showOnlyHeldPositions": False,
    }
    actual = _make_search_payload(
        FILER_FIRST_NAME, FILER_LAST_NAME, FILING_YEAR, FILER_POSITION, False, False
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
            {"queryField": "FilingType", "filterValue": []},
            {"queryField": "FilingYear", "filterValue": "YEAR"},
        ],
        "showOnlyHeldPositions": True,
    }
    actual = _make_search_payload(
        FILER_FIRST_NAME, FILER_LAST_NAME, FILING_YEAR, FILER_POSITION, True, False
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
            {"queryField": "FilingType", "filterValue": []},
            {"queryField": "FilingYear", "filterValue": "YEAR"},
            {"queryField": "Amendment", "filterValue": "true"},
        ],
        "showOnlyHeldPositions": False,
    }
    actual = _make_search_payload(
        FILER_FIRST_NAME, FILER_LAST_NAME, FILING_YEAR, FILER_POSITION, False, True
    )
    assert actual == _EXPECTED
