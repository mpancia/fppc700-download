from __future__ import annotations

from urllib.parse import quote

from .models import Document, FilingPosition


def format_pdf_file_name(document: Document, filing_position: FilingPosition) -> str:
    last = document.filer.last_name.strip()
    first = document.filer.first_name.strip()
    agency = quote(filing_position.agency.replace(" Court", "")).strip()
    position = filing_position.position.strip()
    filing_type = filing_position.filing_type.value.strip()
    filed_date = document.filing_info.filed_date[:10]
    fname = (
        f"{last}_{first}_{filing_position.filing_year}_{agency}_{position}"
        f"_{filing_type}_{filed_date}.pdf"
    )
    # filter out all non-alphanumeric characters, such as '/', '+', '%' and the like.
    fname = fname.replace("%20", "_").replace(" ", "_")
    while not fname[0].isalnum():
        fname = fname[1:]
    while not fname[-1].isalnum():
        fname = fname[:-1]
    fname = "".join([c for c in fname if c.isalnum() or c in ["_", "."]])
    return fname
