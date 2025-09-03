"""
obo_parser.py
==============

Parses Sequence Ontology (SO) OBO files and extracts valid feature types for GFF3 files.

This module provides utilities to:
    - Parse OBO files into term objects
    - Find all descendants of a given SO term (e.g., sequence_feature)
    - Filter valid types for GFF3 features
    - Write valid types to a file for fast lookup
    - Load valid types from a pre-parsed file

References
----------
Sequence Ontology: https://www.sequenceontology.org/
GFF3 Specification: https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md
"""

import re
from pathlib import Path

MODULE_DIR = Path(__file__).parent.resolve()
SO_ONTOLOGIES_PATH = MODULE_DIR / "so_ontologies.obo"
PRE_PARSED_TYPES_PATH = MODULE_DIR / "pre_parsed_valid_types.txt"


class OboTerm:
    """
    Represents a term in an OBO ontology.

    Parameters
    ----------
    id_ : str or None
        The SO accession number for the term.
    name : str or None
        The name of the term.
    is_a : list of str or None
        List of parent SO accession numbers (is_a relationships).
    """

    def __init__(
        self,
        id_: str | None,
        name: str | None,
        is_a: list[str] | None = None,
        synonyms: list[str] | None = None,
    ) -> None:
        self.id: str | None = id_
        self.name: str | None = name
        self.is_a: list[str] = is_a if is_a is not None else []  # list of parent IDs
        self.synonyms: list[str] = synonyms if synonyms is not None else []


def parse_obo(filepath: Path) -> dict[str, OboTerm]:
    """
    Parses an OBO file and returns a dictionary of OboTerm objects.

    Parameters
    ----------
    filepath : Path
        Path to the OBO file.

    Returns
    -------
    dict of str to OboTerm
        Dictionary mapping SO accession numbers to OboTerm objects.
    """
    terms: dict[str, OboTerm] = {}
    current: OboTerm | None = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if current and current.id:
                    terms[current.id] = current
                current = OboTerm(None, None, [])
            elif line.startswith("id: ") and current:
                current.id = line.split("id: ", 1)[1]
            elif line.startswith("name: ") and current:
                current.name = line.split("name: ", 1)[1]
            elif line.startswith("is_a: ") and current:
                parent = line.split("is_a: ", 1)[1].split()[0]
                current.is_a.append(parent)
            elif line.startswith("synonym: ") and current:
                match = re.search(r'"([^"]+)"', line)
                if match:
                    current.synonyms.append(match.group(1))
        if current and current.id:
            terms[current.id] = current
    return terms


def get_descendants(terms: dict[str, OboTerm], root_id: str) -> set[str]:
    """
    Finds all descendants of a given root term in the ontology.

    Parameters
    ----------
    terms : dict of str to OboTerm
        Dictionary of OboTerm objects.
    root_id : str
        SO accession number of the root term.

    Returns
    -------
    set of str
        Set of SO accession numbers that are descendants of the root term (including root).
    """
    descendants: set[str] = set()
    stack: list[str] = [root_id]
    while stack:
        node = stack.pop()
        descendants.add(node)
        for term_id, term in terms.items():
            if node in term.is_a and term_id not in descendants:
                stack.append(term_id)
    return descendants


def filter_types(obo_path: Path) -> list[tuple[str, str]]:
    """
    Filters valid SO types for GFF3 features from an OBO file.

    Parameters
    ----------
    obo_path : str
        Path to the OBO file.

    Returns
    -------
    list of tuple of (str, str)
        List of (SO accession, name) pairs for valid types (descendants of sequence_feature).
    """
    terms = parse_obo(obo_path)
    valid_ids = get_descendants(terms, "SO:0000110")
    valid_types: list[tuple[str, str]] = []
    for tid in valid_ids:
        if tid in terms:
            term = terms[tid]
            if term.name:
                valid_types.append((tid, str(term.name)))
            for syn in term.synonyms:
                valid_types.append((tid, syn))
    return valid_types


def write_out_valid_types(valid_types: list[tuple[str, str]], output_path: Path) -> None:
    """
    Writes valid SO types to a file in tab-separated format.

    Parameters
    ----------
    valid_types : list of tuple of (str, str)
        List of (SO accession, name) pairs to write.
    output_path : str
        Path to the output file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for tid, name in valid_types:
            f.write(f"{tid}\t{name}\n")


def main() -> None:
    """
    Main function to parse the OBO file and write valid types to output.
    """
    valid_types = filter_types(SO_ONTOLOGIES_PATH)
    write_out_valid_types(valid_types, PRE_PARSED_TYPES_PATH)


def get_valid_types() -> list[str]:
    """
    Loads valid SO types from the pre-parsed output file.

    Summary
    -------
    In the GFF3 specification, the 'type' field for a feature must be a Sequence Ontology (SO) term or accession number.
    Valid types are 'sequence_feature' (SO:0000110) or any is_a descendant of it, as defined in the SO OBO file.

    Returns
    -------
    dict of str to str
        Dictionary mapping SO accession numbers to names.
    """
    types: list[str] = []
    with open(PRE_PARSED_TYPES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                _, name = line.split("\t", 1)
                types.append(name.strip().lower())
    return types


if __name__ == "__main__":
    main()
