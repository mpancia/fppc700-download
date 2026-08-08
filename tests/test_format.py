from fppc700download.format import format_pdf_file_name

FILER_LAST_NAME = "LAST"
FILER_FIRST_NAME = "FIRST"
FILER_AGENCY = "AGENCY"
FILER_POSITION = "POSITION"
FILING_TYPE = "TYPE"
FILING_YEAR = "YEAR"
FILED_DATE = "2026-04-21T16:36:19"


def test_format_pdf_file_name():
    _EXPECTED = """LAST_FIRST_YEAR_AGENCY_POSITION_TYPE_20260421.pdf"""
    actual = format_pdf_file_name(
        FILER_LAST_NAME,
        FILER_FIRST_NAME,
        FILER_AGENCY,
        FILER_POSITION,
        FILING_TYPE,
        FILING_YEAR,
        FILED_DATE,
    )
    assert actual == _EXPECTED


def test_format_pdf_file_name_removes_court():
    _EXPECTED = """LAST_FIRST_YEAR_AGENCY_POSITION_TYPE_20260421.pdf"""
    actual = format_pdf_file_name(
        FILER_LAST_NAME,
        FILER_FIRST_NAME,
        "AGENCY Court",
        FILER_POSITION,
        FILING_TYPE,
        FILING_YEAR,
        FILED_DATE,
    )
    assert actual == _EXPECTED


def test_format_pdf_file_name_replace_space_with_underscore():
    _EXPECTED = """LAST_FIRST_YEAR_AGENCY_TWO_POSITION_TYPE_20260421.pdf"""
    actual = format_pdf_file_name(
        FILER_LAST_NAME,
        FILER_FIRST_NAME,
        "AGENCY TWO",
        FILER_POSITION,
        FILING_TYPE,
        FILING_YEAR,
        FILED_DATE,
    )
    assert actual == _EXPECTED


def test_format_pdf_file_name_remove_hyphen():
    _EXPECTED = """LAST_FIRST_YEAR_AGENCYTWO_POSITION_TYPE_20260421.pdf"""
    actual = format_pdf_file_name(
        FILER_LAST_NAME,
        FILER_FIRST_NAME,
        "AGENCY-TWO",
        FILER_POSITION,
        FILING_TYPE,
        FILING_YEAR,
        FILED_DATE,
    )
    assert actual == _EXPECTED


def test_format_pdf_file_name_remove_leading_non_alphanumeric():
    _EXPECTED = """LAST_FIRSTNAME_YEAR_AGENCY_POSITION_TYPE_20260421.pdf"""
    actual = format_pdf_file_name(
        "+LAST+",
        "+FIRST+NAME+",
        FILER_AGENCY,
        FILER_POSITION,
        FILING_TYPE,
        FILING_YEAR,
        FILED_DATE,
    )
    assert actual == _EXPECTED


def test_format_pdf_file_name_remove_city_slash_town():
    _EXPECTED = """LAST_FIRST_YEAR_Agency_CityTown_POSITION_TYPE_20260421.pdf"""
    actual = format_pdf_file_name(
        "+LAST+",
        FILER_FIRST_NAME,
        "Agency City/Town",
        FILER_POSITION,
        FILING_TYPE,
        FILING_YEAR,
        FILED_DATE,
    )
    assert actual == _EXPECTED


def test_format_pdf_file_name_disambiguates_amendment():
    original = format_pdf_file_name(
        FILER_LAST_NAME,
        FILER_FIRST_NAME,
        FILER_AGENCY,
        FILER_POSITION,
        FILING_TYPE,
        FILING_YEAR,
        "2026-03-03T12:30:23",
    )
    amendment = format_pdf_file_name(
        FILER_LAST_NAME,
        FILER_FIRST_NAME,
        FILER_AGENCY,
        FILER_POSITION,
        FILING_TYPE,
        FILING_YEAR,
        FILED_DATE,
    )
    assert original != amendment
