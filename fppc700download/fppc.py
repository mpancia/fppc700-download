import json

import requests


def _make_download_payload(
    filer_last_name,
    filer_first_name,
    filer_agency,
    filer_position,
    filing_year,
    filing_type,
    document_index_id,
):
    payload = {
        "formInfo": {
            "LastName": filer_last_name,
            "FirstName": filer_first_name,
            "Agency": filer_agency,
            "Position": filer_position,
            "FilingYear": filing_year,
            "FilingType": filing_type,
        },
        "indexID": document_index_id,
    }
    return payload


def download_document(
    filer_last_name,
    filer_first_name,
    filer_agency,
    filer_position,
    filing_type,
    filing_year,
    document_index_id,
    output_directory,
    file_name,
):
    cookie_key = "ASP.NET_SessionId"
    url = "https://form700search.fppc.ca.gov/Home/GetRedactedFormPdf"
    payload = _make_download_payload(
        filer_last_name,
        filer_first_name,
        filer_agency,
        filer_position,
        filing_year,
        filing_type,
        document_index_id,
    )

    file_url_response = requests.post(
        url, headers={"content-type": "application/json"}, data=json.dumps(payload)
    )
    file_url_response.raise_for_status()
    file_url_response_json = file_url_response.json()
    document_url = file_url_response_json["PDFDownloadUrl"]
    session_id_cookie = file_url_response.cookies[cookie_key]
    jar = requests.cookies.RequestsCookieJar()
    jar.set(cookie_key, session_id_cookie)

    file_response = requests.get(document_url, cookies=jar)
    file_response.raise_for_status()

    file_path = f"{output_directory.rstrip('/')}/{file_name}"

    with open(file_path, "wb") as file:
        for chunk in file_response.iter_content(chunk_size=16 * 1024):
            file.write(chunk)

    file.close()

    return document_url


def _make_search_payload(
    filer_first_name,
    filer_last_name,
    filer_agency,
    filing_year,
    filer_position,
    currently_held_positions_only,
    amendments_only,
):
    payload = {
        "queryGenerationInfo": None,
        "searchFieldQueryInfos": [],
        "showOnlyHeldPositions": currently_held_positions_only,
    }

    if filer_position != "":
        payload["searchFieldQueryInfos"].append(
            {"queryField": "FilerPosition", "filterValue": filer_position},
        )

    if filer_first_name != "":
        payload["searchFieldQueryInfos"].append(
            {
                "queryField": "FilerFirstName",
                "queryType": "Start With",
                "filterValue": filer_first_name,
            }
        )

    if filer_last_name != "":
        payload["searchFieldQueryInfos"].append(
            {
                "queryField": "FilerLastName",
                "queryType": "Start With",
                "filterValue": filer_last_name,
            }
        )

    if filer_agency != "":
        payload["searchFieldQueryInfos"].append(
            {
                "queryField": "FilerAgency",
                "filterValue": filer_agency,
            }
        )

    payload["searchFieldQueryInfos"].append(
        {"queryField": "FilingType", "filterValue": []}
    )

    if filing_year != "":
        payload["searchFieldQueryInfos"].append(
            {"queryField": "FilingYear", "filterValue": filing_year}
        )

    if amendments_only:
        payload["searchFieldQueryInfos"].append(
            {"queryField": "Amendment", "filterValue": "true"}
        )
    return payload


def search_for_documents(
    filer_first_name,
    filer_last_name,
    filer_agency,
    filing_year,
    filer_position,
    currently_held_positions_only,
    amendments_only,
):
    url = "https://form700search.fppc.ca.gov/Home/SearchDocuments"

    payload = _make_search_payload(
        filer_first_name,
        filer_last_name,
        filer_agency,
        filing_year,
        filer_position,
        currently_held_positions_only,
        amendments_only,
    )
    r = requests.post(url, data=json.dumps(payload))
    r.raise_for_status()
    documents = json.loads(json.loads(r.text))
    return documents
