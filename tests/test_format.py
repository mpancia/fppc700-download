from fppc700download.format import format_pdf_file_name
from fppc700download.models import (
    Document,
    Filer,
    FilingInfo,
    FilingPosition,
    FilingType,
)

FILER_LAST_NAME = "LAST"
FILER_FIRST_NAME = "FIRST"
FILER_AGENCY = "AGENCY"
FILER_POSITION = "POSITION"
FILING_YEAR = "YEAR"
FILED_DATE = "2026-04-21T16:36:19"


def _make(
    last_name=FILER_LAST_NAME,
    first_name=FILER_FIRST_NAME,
    agency=FILER_AGENCY,
    filed_date=FILED_DATE,
    is_amendment=False,
):
    document = Document(
        index_id="FAKE-ID",
        filer=Filer(last_name=last_name, first_name=first_name),
        filing_info=FilingInfo(
            filed_date=filed_date,
            is_amendment=is_amendment,
            no_reportable_interests=False,
        ),
        filing_positions=[],
    )
    position = FilingPosition(
        agency=agency,
        position=FILER_POSITION,
        filing_type=FilingType.ANNUAL,
        filing_year=FILING_YEAR,
    )
    return document, position


def test_format_pdf_file_name():
    _EXPECTED = """LAST_FIRST_YEAR_AGENCY_POSITION_Annual_20260421.pdf"""
    actual = format_pdf_file_name(*_make())
    assert actual == _EXPECTED


def test_format_pdf_file_name_removes_court():
    _EXPECTED = """LAST_FIRST_YEAR_AGENCY_POSITION_Annual_20260421.pdf"""
    actual = format_pdf_file_name(*_make(agency="AGENCY Court"))
    assert actual == _EXPECTED


def test_format_pdf_file_name_replace_space_with_underscore():
    _EXPECTED = """LAST_FIRST_YEAR_AGENCY_TWO_POSITION_Annual_20260421.pdf"""
    actual = format_pdf_file_name(*_make(agency="AGENCY TWO"))
    assert actual == _EXPECTED


def test_format_pdf_file_name_remove_hyphen():
    _EXPECTED = """LAST_FIRST_YEAR_AGENCYTWO_POSITION_Annual_20260421.pdf"""
    actual = format_pdf_file_name(*_make(agency="AGENCY-TWO"))
    assert actual == _EXPECTED


def test_format_pdf_file_name_remove_leading_non_alphanumeric():
    _EXPECTED = """LAST_FIRSTNAME_YEAR_AGENCY_POSITION_Annual_20260421.pdf"""
    actual = format_pdf_file_name(*_make(last_name="+LAST+", first_name="+FIRST+NAME+"))
    assert actual == _EXPECTED


def test_format_pdf_file_name_remove_city_slash_town():
    _EXPECTED = """LAST_FIRST_YEAR_Agency_CityTown_POSITION_Annual_20260421.pdf"""
    actual = format_pdf_file_name(*_make(last_name="+LAST+", agency="Agency City/Town"))
    assert actual == _EXPECTED


def test_format_pdf_file_name_disambiguates_amendment():
    original = format_pdf_file_name(*_make(filed_date="2026-03-03T12:30:23"))
    amendment = format_pdf_file_name(
        *_make(filed_date="2026-04-21T16:36:19", is_amendment=True)
    )
    assert original != amendment


def test_format_pdf_file_name_labels_amendment():
    _EXPECTED = """LAST_FIRST_YEAR_AGENCY_POSITION_Annual_Amendment_20260421.pdf"""
    actual = format_pdf_file_name(*_make(is_amendment=True))
    assert actual == _EXPECTED
