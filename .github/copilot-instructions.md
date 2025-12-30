# Biovalid AI Assistant Instructions

## Project Overview
Biovalid is a lightweight Python library for validating bioinformatics files (FASTA, FASTQ, BAM, BAI, GFF). It's designed with no external dependencies and follows a plugin-style validator architecture.

## Core Architecture

### Validator Pattern
- All validators inherit from `BaseValidator` in `biovalid/validators/base.py`
- Each file type has its own validator class (e.g., `FastaValidator`, `BamValidator`)
- Validators are selected dynamically via `FileType.from_path()` enum in `biovalid/enum.py`
- Two-stage validation: `general_validation()` (existence, readability) + `validate()` (format-specific)

### File Type Detection
- `FileType` enum handles extension mapping (including compressed files like `.fasta.gz`)
- Compression detection strips outer extension to find true file type
- Magic byte validation for binary formats (BAM, BAI) using `MagicBytes` enum

### Error Handling Philosophy
- Uses logging levels for validation results: ERROR (40) = validation failure
- `log_function()` in `logger.py` raises `ValueError` on ERROR level
- Bool mode catches exceptions to return True/False instead of raising

## Key Patterns

### Adding New Validators
1. Create validator in `biovalid/validators/` inheriting from `BaseValidator`
2. Add file extensions to `FileType` enum
3. Register validator in `biovalidator.py` `file_type_dict`
4. Import in `biovalid/validators/__init__.py`

### Binary File Validation
- Use magic bytes from `MagicBytes` enum for format verification
- Read files in binary mode with chunked processing (see `fasta.py` for example)
- Handle compressed files through extension stripping, not decompression

### GFF/Ontology Integration
- GFF validation uses Sequence Ontology (SO) terms from `biovalid/util/gff/`
- Pre-parsed valid types in `pre_parsed_valid_types.txt` for performance
- OBO parser extracts descendants of `sequence_feature` (SO:0000110)

## Development Workflows

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/        # Unit tests
pytest tests/e2e/         # End-to-end tests

# Use tox for multi-environment testing
tox -e 3.11,3.12,3.13    # Test Python versions
tox -e format            # Code formatting
tox -e lint              # Linting
```

### Code Quality
- Black + isort for formatting: `tox -e format`
- Pylint + mypy for linting: `tox -e lint`
- Strict typing enforced (mypy config in `pyproject.toml`)
- Line length: 150 characters
- Pylint score threshold: 9.0

### CLI vs Library Usage
- CLI entry point: `python -m biovalid` → `biovalidator.run_cli()`
- Library usage: `from biovalid import BioValidator`
- Both modes share same validation logic through `BioValidator` class

## Critical Implementation Details

### Path Handling
- Always use `Path` objects internally
- Support both files and directories (with recursive option)
- Filter unknown file types automatically during directory scanning

### Logging Configuration
- Named logger "biovalid" with structured formatting
- Console + optional file output
- Verbose mode enables DEBUG level
- Critical: flush/close handlers on exceptions to ensure log persistence

### Performance Considerations
- Chunked binary file reading (8192 bytes) for large files
- Pre-parsed ontology files to avoid runtime OBO parsing
- Enum-based type detection for fast file classification

## File Organization
- `biovalid/`: Core library code
- `biovalid/validators/`: File type validators
- `biovalid/util/gff/`: GFF-specific utilities and ontologies
- `tests/data/`: Test fixtures organized by file type
- `tests/unit/` vs `tests/e2e/`: Unit vs integration tests