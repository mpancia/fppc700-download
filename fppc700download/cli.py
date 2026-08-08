from os import listdir, makedirs

import click
from progress.bar import Bar

from .format import format_pdf_file_name
from .fppc import download_document, search_for_documents


@click.command()
@click.option(
    "--filer-first-name", default="", help="First name starts with search query"
)
@click.option(
    "--filer-last-name", default="", help="Last name starts with search query"
)
@click.option("--filer-agency", default="", help="Agency to search")
@click.option(
    "--filer-position",
    default="",
    help='Filer\'s position such as "Governor" or "Assembly Member" or "Senator"',
)
@click.option("--filing-year", default="", help="Year for data in report")
@click.option(
    "--output-directory",
    default=".",
    help="Path to destination directory of PDF files, default is .",
)
@click.option(
    "--amendments-only", is_flag=True, help="Only search for Amendment filings"
)
@click.option(
    "--currently-held-positions-only",
    is_flag=True,
    help="Limit to reports by filers with a current position",
)
@click.option(
    "--ignore-existing-files",
    is_flag=True,
    help="Only download files that don't exist in output directory",
)
def search_and_download_documents(
    filer_first_name,
    filer_last_name,
    filer_agency,
    filer_position,
    filing_year,
    output_directory,
    amendments_only,
    ignore_existing_files,
    currently_held_positions_only,
):

    found_documents = search_for_documents(
        filer_first_name,
        filer_last_name,
        filer_agency,
        filing_year,
        filer_position,
        currently_held_positions_only,
        amendments_only,
    )
    documents = found_documents["documents"]
    documents_count = found_documents["total"]

    if documents_count == 0:
        print("No documents found")
        return

    if documents_count > 1000:
        print(
            f"WARNING: {documents_count} documents found but FPPC returns a maximum of 1,000 rows; try further limiting your search"
        )

    makedirs(output_directory, exist_ok=True)
    existing_files = listdir(output_directory)

    bar = Bar("Processing and downloading", max=len(documents))
    for document in documents:
        document_filer_last_name = document["filer"]["lastName"]
        document_filer_first_name = document["filer"]["firstName"]
        document_filer_agency = document["filingPositions"][0]["agency"]
        document_filer_position = document["filingPositions"][0]["position"]
        document_filing_type = document["filingPositions"][0]["filingType"]
        document_filing_year = document["filingPositions"][0]["filingYear"]
        document_filed_date = document["filingInfo"]["filedDate"]
        document_index = document["indexID"]

        # "Retired Judge" gets returned with "Judge", filter it out
        if filer_position == "Judge" and document_filer_position == "Retired Judge":
            bar.next()
            continue

        expected_file_name = format_pdf_file_name(
            document_filer_last_name,
            document_filer_first_name,
            document_filer_agency,
            document_filer_position,
            document_filing_type,
            document_filing_year,
            document_filed_date,
        )

        if ignore_existing_files and expected_file_name in existing_files:
            bar.next()
            continue

        download_document(
            document_filer_last_name,
            document_filer_first_name,
            document_filer_agency,
            document_filer_position,
            document_filing_type,
            document_filing_year,
            document_index,
            output_directory,
            expected_file_name,
        )

        bar.next()
    bar.finish()
