from argparse import ArgumentParser, Namespace

from biovalid.logger import validate_log_file
from biovalid.version import __version__


def cli_parser() -> Namespace:
    parser = ArgumentParser(
        prog="biovalid",
        description="A tool for validating bioinformatics files.",
        epilog="For more information, visit https://github.com/RIVM-bioinformatics/biovalid",
    )
    parser.add_argument(
        "file_paths",
        nargs="+",
        type=str,
        help="One or more file paths to validate. Can be compressed files. Can also be a directory containing files.",
    )

    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        default=False,
        help="Recursively validate all files in a directory.",
    )

    parser.add_argument(
        "--bool-mode",
        "-b",
        action="store_true",
        default=False,
        help="Return True if all files are valid, False if any file is invalid.",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose output.",
    )

    parser.add_argument(
        "--log-file",
        "-l",
        type=validate_log_file,
        default=None,
        help="Path to a log file.",
    )

    parser.add_argument(
        "--bed",
        choices=("3", "4", "5", "6", "7", "8", "9", "12", "auto"),
        default="auto",
        help="BED tier. 'auto' (default) picks the max N for the actual column count. "
             "An explicit N (3-9 or 12) validates cols 1-N and treats the rest as opaque "
             "custom data (use for narrowPeak, broadPeak, bedmethyl).",
    )

    parser.add_argument(
        "--spec",
        choices=("ucsc", "hts"),
        default="ucsc",
        help="BED spec to validate against. 'ucsc' (default) follows the UCSC FAQ; "
             "'hts' enforces the stricter hts-specs BEDv1 literal.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version of biovalid.",
    )

    return parser.parse_args()
