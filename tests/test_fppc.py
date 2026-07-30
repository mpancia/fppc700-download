from fppc700download.fppc import make_pdf_file_name

FILER_LAST_NAME = 'LAST'
FILER_FIRST_NAME = 'FIRST'
FILER_AGENCY = 'AGENCY'
FILER_POSITION = 'POSITION'
FILING_TYPE = 'TYPE'
FILING_YEAR = 'YEAR'


def test_make_pdf_file_name():
    _EXPECTED = '''LAST_FIRST_YEAR_AGENCY_POSITION_TYPE.pdf'''
    actual = make_pdf_file_name(FILER_LAST_NAME, FILER_FIRST_NAME,
                                FILER_AGENCY, FILER_POSITION, FILING_TYPE, FILING_YEAR)
    assert actual == _EXPECTED


def test_make_pdf_file_name_removes_court():
    _EXPECTED = '''LAST_FIRST_YEAR_AGENCY_POSITION_TYPE.pdf'''
    actual = make_pdf_file_name(FILER_LAST_NAME, FILER_FIRST_NAME,
                                'AGENCY Court', FILER_POSITION, FILING_TYPE, FILING_YEAR)
    assert actual == _EXPECTED


def test_make_pdf_file_name_replace_space_with_underscore():
    _EXPECTED = '''LAST_FIRST_YEAR_AGENCY_TWO_POSITION_TYPE.pdf'''
    actual = make_pdf_file_name(FILER_LAST_NAME, FILER_FIRST_NAME,
                                'AGENCY TWO', FILER_POSITION, FILING_TYPE, FILING_YEAR)
    assert actual == _EXPECTED


def test_make_pdf_file_name_remove_hyphen():
    _EXPECTED = '''LAST_FIRST_YEAR_AGENCYTWO_POSITION_TYPE.pdf'''
    actual = make_pdf_file_name(FILER_LAST_NAME, FILER_FIRST_NAME,
                                'AGENCY-TWO', FILER_POSITION, FILING_TYPE, FILING_YEAR)
    assert actual == _EXPECTED


def test_make_pdf_file_name_remove_leading_non_alphanumeric():
    _EXPECTED = '''LAST_FIRSTNAME_YEAR_AGENCY_POSITION_TYPE.pdf'''
    actual = make_pdf_file_name(
        "+LAST+", "+FIRST+NAME+", FILER_AGENCY, FILER_POSITION, FILING_TYPE, FILING_YEAR)
    assert actual == _EXPECTED

def test_make_pdf_file_name_remove_city_slash_town():
    _EXPECTED = '''LAST_FIRST_YEAR_Agency_CityTown_POSITION_TYPE.pdf'''
    actual = make_pdf_file_name(
        "+LAST+", FILER_FIRST_NAME, "Agency City/Town", FILER_POSITION, FILING_TYPE, FILING_YEAR)
    assert actual == _EXPECTED