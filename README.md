<div align="center">
    <h1>Biovalid</h1>
    <br />
    <h2>Quick validation of bioinformatics files</h2>
    <br />
</div>

## Pipeline information
* **Author(s):**            Gino Raaijmakers
* **Organization:**         Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
* **Department:**           Infectieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Informatiebeheer (IBR)
* **Start date:**           23 - 07 - 2025

## About this project
**Biovalid** is a lightweight Python library and CLI tool for fast, robust validation of bioinformatics files such as BAM, FASTA, and GFF. It checks file integrity, headers, and format compliance, helping users catch common issues before downstream analysis.


---

## Features

- **File Format Support**: Validate BAM/BAI, FASTA/FASTQ, VCF and GFF files.
- **Lightweight**: No dependencies.
- **Dual Usage**: Use as a CLI tool or import as a Python library.
- **Customizable**: Enable verbose logging, save logs to a file, or return boolean results.
- **Extensible**: Designed to support additional file formats in the future.


---

## Installation

### Conda
```bash
conda create -n biovalid python>=3.10
conda activate biovalid
pip install biovalid
```
### Pip
```bash
pip install biovalid
```

---

## Parameters & Usage

### Command-line help
```
python3 -m biovalid --help
```

### Required parameters
* `-i, --input` Path to the file or directory to validate

### Optional parameters
* `-v, --verbose` Enable verbose logging
* `-l, --log_file` Path to a log file
* `-r, --recursive` Recursively validate files in directories
* `-t, --threads` Number of threads to use for validation
* `-R, --raise` Raise an exception when validation fails

### Example command
```bash
python3 -m biovalid -i /path/to/file.bam
```

### Library usage
```python
from biovalid import BioValidator

validator = BioValidator(verbose=True)
validator.validate_files("path/to/file")
```
---

## Output
* **Logging:** Validation results and errors are printed to the console and optionally saved to a log file.
* **Return values:** Returns `True` if all files are valid, `False` otherwise.
---

## Issues
---

## Future ideas
* Add support for more file formats (e.g., SAM, Phylip, genbank).
* Improve error messages and reporting.
* Make the tool more user-friendly for external users.

---

## License
This project is licensed under the AGPL-3.0 license. See the [LICENSE](LICENSE) file for details.

---

## Contact
* **Contact person:** Gino Raaijmakers
* **Email:** gino.raaijmakers@rivm.nl

---

## Acknowledgements
Thanks to the IDS and IBR teams at RIVM for their support and feedback.