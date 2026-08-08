import logging
from pathlib import Path

import click
from progress.bar import Bar

from .format import format_pdf_file_name
from .fppc import download_document, search_for_documents

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


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
    type=click.Path(file_okay=False, path_type=Path),
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
    filer_first_name: str,
    filer_last_name: str,
    filer_agency: str,
    filer_position: str,
    filing_year: str,
    output_directory: Path,
    amendments_only: bool,
    ignore_existing_files: bool,
    currently_held_positions_only: bool,
) -> None:
    result = search_for_documents(
        filer_first_name,
        filer_last_name,
        filer_agency,
        filing_year,
        filer_position,
        currently_held_positions_only,
        amendments_only,
    )

    if result.total == 0:
        logger.info("No documents found")
        return

    if result.total > 1000:
        logger.warning(
            "%s documents found but FPPC returns a maximum of 1,000 rows; try further limiting your search",
            result.total,
        )

    output_directory.mkdir(parents=True, exist_ok=True)
    existing_files = {path.name for path in output_directory.iterdir()}

    bar = Bar("Processing and downloading", max=len(result.documents))
    for document in result.documents:
        position = document.filing_positions[0]

        if filer_position != "" and position.position != filer_position:
            bar.next()
            continue

        expected_file_name = format_pdf_file_name(document, position)

        if ignore_existing_files and expected_file_name in existing_files:
            bar.next()
            continue

        download_document(
            document.filer.last_name,
            document.filer.first_name,
            position.agency,
            position.position,
            position.filing_type,
            position.filing_year,
            document.index_id,
            output_directory,
            expected_file_name,
        )

        bar.next()
    bar.finish()
