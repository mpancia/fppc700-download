from fppc700download.models import (
    Document,
    FilingType,
    SearchResult,
    matching_filing_positions,
)

DOCUMENT = {
    "filingInfo": {
        "noReportableInterests": False,
        "isAmendment": True,
        "filedDate": "2026-04-01T17:19:08",
    },
    "filer": {"lastName": "Mandelman", "firstName": "Rafael"},
    "indexID": "7479ecaf-cf56-417c-815f-4daca05f4507",
    "filingPositions": [
        {
            "agency": "City and County of San Francisco",
            "dueDate": "04/01/2026",
            "filingType": "Annual",
            "filingYear": 2025,
            "position": "Supervisor",
        },
        {
            "agency": "Transbay Joint Powers Authority",
            "dueDate": "04/01/2026",
            "filingType": "Annual",
            "filingYear": 2025,
            "position": "Members of the Board of Directors",
        },
    ],
}


def test_document_from_api():
    document = Document.from_api(DOCUMENT)

    assert document.index_id == "7479ecaf-cf56-417c-815f-4daca05f4507"
    assert document.filer.last_name == "Mandelman"
    assert document.filer.first_name == "Rafael"
    assert document.filer.middle_name is None
    assert document.filing_info.is_amendment is True
    assert document.filing_info.filed_date == "2026-04-01T17:19:08"
    assert len(document.filing_positions) == 2
    assert document.filing_positions[0].agency == "City and County of San Francisco"
    assert document.filing_positions[0].filing_type == FilingType.ANNUAL
    assert document.filing_positions[1].position == "Members of the Board of Directors"


def test_filer_middle_name_is_optional():
    document = Document.from_api(
        {
            **DOCUMENT,
            "filer": {
                "lastName": "Melgar",
                "firstName": "Myrna",
                "middleName": "Elizabeth",
            },
        }
    )

    assert document.filer.middle_name == "Elizabeth"


def test_search_result_from_api():
    result = SearchResult.from_api({"total": 1, "documents": [DOCUMENT]})

    assert result.total == 1
    assert len(result.documents) == 1
    assert result.documents[0].index_id == DOCUMENT["indexID"]


def test_matching_filing_positions_filters_by_position():
    document = Document.from_api(DOCUMENT)

    matches = matching_filing_positions(document, "", "Supervisor")

    assert [m.agency for m in matches] == ["City and County of San Francisco"]


def test_matching_filing_positions_filters_by_agency():
    document = Document.from_api(DOCUMENT)

    matches = matching_filing_positions(document, "Transbay Joint Powers Authority", "")

    assert [m.position for m in matches] == ["Members of the Board of Directors"]


def test_matching_filing_positions_no_filter_returns_all():
    document = Document.from_api(DOCUMENT)

    matches = matching_filing_positions(document, "", "")

    assert len(matches) == 2


def test_matching_filing_positions_no_match_returns_empty():
    document = Document.from_api(DOCUMENT)

    matches = matching_filing_positions(document, "", "Treasurer")

    assert matches == []
