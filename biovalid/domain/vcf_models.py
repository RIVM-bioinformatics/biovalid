"""Module to store all necessary VCF models."""

from dataclasses import dataclass
from enum import Enum


class VCFHeaders(Enum):
    """
    Standard VCF file headers as per VCF specification.
    More information can be found at: https://github.com/samtools/hts-specs

    Other headers can be defined by users as needed.
    """

    CHROM = "CHROM"
    POS = "POS"
    ID = "ID"
    REF = "REF"
    ALT = "ALT"
    QUAL = "QUAL"
    FILTER = "FILTER"
    INFO = "INFO"
    FORMAT = "FORMAT"  # optional
    # and then sample IDs follow FORMAT


class AltTypes(Enum):
    """Standard ALT field types in VCF files."""

    DEL = "DEL"
    INS = "INS"
    DUP = "DUP"
    INV = "INV"
    CNV = "CNV"
    DUP_TANDEM = "DUP:TANDEM"
    DEL_ME = "DEL:ME"
    INS_ME = "INS:ME"


@dataclass
class InfoField:
    """Class to store InfoField details."""

    id: str
    number: str
    type: str
    description: str
    # optionals
    source: str = ""
    version: str = ""
    extra: dict[str, str] | None = None


@dataclass
class FilterField:
    """Class to store FilterField details."""

    id: str
    description: str
    # optional
    extra: dict[str, str] | None = None


@dataclass
class FormatField:
    """Class to store FormatField details."""

    id: str
    number: str
    type: str
    description: str
    # optional
    extra: dict[str, str] | None = None


@dataclass
class AltField:
    """Class to store AltField details."""

    id: AltTypes
    description: str
    # optional
    extra: dict[str, str] | None = None
