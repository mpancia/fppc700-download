from urllib.parse import quote


def format_pdf_file_name(
    filer_last_name,
    filer_first_name,
    filer_agency,
    filer_position,
    filing_type,
    filing_year,
):
    last = filer_last_name.strip()
    first = filer_first_name.strip()
    agency = quote(filer_agency.replace(" Court", "")).strip()
    position = filer_position.strip()
    filing_type = filing_type.strip()
    fname = f"{last}_{first}_{filing_year}_{agency}_{position}_{filing_type}.pdf"
    # filter out all non-alphanumeric characters, such as '/', '+', '%' and the like.
    fname = fname.replace("%20", "_").replace(" ", "_")
    while not fname[0].isalnum():
        fname = fname[1:]
    while not fname[-1].isalnum():
        fname = fname[:-1]
    fname = "".join([c for c in fname if c.isalnum() or c in ["_", "."]])
    return fname
