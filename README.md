<div align="center">
    <h1>Biovalid</h1>
    <br />
    <h2>Quick validation of bioinformatics files</h2>
    <br />
    <img src="https://via.placeholder.com/150" alt="pipeline logo">
</div>

## Pipeline information
* **Author(s):**            Gino Raaijamkers
* **Organization:**         Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
* **Department:**           Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Informatiebeheer (IBR)
* **Start date:**           23 - 07 - 2025

## About this project
**Biovalid** is a Python library and CLI tool for fast, robust validation of bioinformatics files such as BAM, FASTA, and FASTQ. It checks file integrity, headers, and format compliance, helping users catch common issues before downstream analysis.


## Prerequisities
* Linux-like environment with (mini) conda installed 
* Python3.7.6


## Installation

### Conda



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
* `-b, --bool_mode` Return True/False instead of raising exceptions

### Example command
```
python3 -m biovalid -i /path/to/file.bam
```

### Library usage
```python
from biovalid import BioValidator

validator = BioValidator(file_paths="/path/to/file.bam", verbose=True)
validator.validate_files()
```

Detailed information about the pipeline can be found in the [documentation](link to other docs). This documentation is only suitable for users that have access to the RIVM Linux environment.

## Output
* **Logging:** Validation results and errors are printed to the console and optionally saved to a log file.
* **Return values:** In bool mode, returns `True` if all files are valid, `False` otherwise.

## Issues

## Future ideas
* Add support for more file formats (e.g., VCF, GFF).
* Improve error messages and reporting.
* Make the tool more user-friendly for external users.

## License
This project is licensed under the AGPL-3.0 license. See the [LICENSE](LICENSE) file for details.

## Contact
* **Contact person:** Gino Raaijmakers
* **Email:** gino.raaijmakers@rivm.nl

## Acknowledgements
Thanks to the IDS and IBR teams at RIVM for their support and feedback.