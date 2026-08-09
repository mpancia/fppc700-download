from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class FilingType(StrEnum):
    ANNUAL = "Annual"
    ASSUMING = "Assuming"
    LEAVING = "Leaving"
    CANDIDATE = "Candidate"


@dataclass(frozen=True, slots=True)
class Filer:
    last_name: str
    first_name: str
    middle_name: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Filer:
        return cls(
            last_name=data["lastName"],
            first_name=data["firstName"],
            middle_name=data.get("middleName"),
        )


@dataclass(frozen=True, slots=True)
class FilingPosition:
    agency: str
    position: str
    filing_type: FilingType
    filing_year: int
    due_date: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> FilingPosition:
        return cls(
            agency=data["agency"],
            position=data["position"],
            filing_type=FilingType(data["filingType"]),
            filing_year=data["filingYear"],
            due_date=data.get("dueDate"),
        )


@dataclass(frozen=True, slots=True)
class FilingInfo:
    filed_date: str
    is_amendment: bool
    no_reportable_interests: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> FilingInfo:
        return cls(
            filed_date=data["filedDate"],
            is_amendment=data["isAmendment"],
            no_reportable_interests=data["noReportableInterests"],
        )


@dataclass(frozen=True, slots=True)
class Document:
    index_id: str
    filer: Filer
    filing_info: FilingInfo
    filing_positions: list[FilingPosition]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Document:
        return cls(
            index_id=data["indexID"],
            filer=Filer.from_api(data["filer"]),
            filing_info=FilingInfo.from_api(data["filingInfo"]),
            filing_positions=[
                FilingPosition.from_api(p) for p in data["filingPositions"]
            ],
        )


@dataclass(frozen=True, slots=True)
class SearchResult:
    total: int
    documents: list[Document]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SearchResult:
        return cls(
            total=data["total"],
            documents=[Document.from_api(d) for d in data["documents"]],
        )


def matching_filing_positions(
    document: Document, filer_agency: str, filer_position: str
) -> list[FilingPosition]:
    return [
        position
        for position in document.filing_positions
        if (filer_agency == "" or position.agency == filer_agency)
        and (filer_position == "" or position.position == filer_position)
    ]
