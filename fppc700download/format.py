from urllib.parse import quote


def format_pdf_file_name(
    filer_last_name,
    filer_first_name,
    filer_agency,
    filer_position,
    filing_type,
    filing_year,
):
    fname = "%s_%s_%s_%s_%s_%s.pdf" % (
        filer_last_name.strip(),
        filer_first_name.strip(),
        filing_year,
        quote(filer_agency.replace(" Court", "")).strip(),
        filer_position.strip(),
        filing_type.strip(),
    )
    # filter out all non-alphanumeric characters, such as '/', '+', '%' and the like.
    fname = fname.replace("%20", "_").replace(" ", "_")
    while not fname[0].isalnum():
        fname = fname[1:]
    while not fname[-1].isalnum():
        fname = fname[:-1]
    fname = "".join([c for c in fname if c.isalnum() or c in ["_", "."]])
    return fname
