"""Command line interface for bibtex2cff."""
import argparse as ap

from pathlib import Path

from bibtex2cff import __version__
from bibtex2cff.convert_cff import CFFDefintionUpdate
from bibtex2cff.convert_cff import save_cff_definition


def cmd() -> ap.Namespace:
    """Parse command line arguments and return a Namespace object."""
    parser = ap.ArgumentParser(
        prog="bibtex2cff",
        description="Converting Bibtex to CITATION.cff fileformat",
        formatter_class=ap.RawDescriptionHelpFormatter,
        epilog="For more information, see: https://github.com/Anselmoo/bibtex2cff",
        usage="bibtex2cff [options] BIBFILE",
    )
    parser.add_argument(
        "bibfile",
        metavar="BIBFILE",
        type=lambda p: Path(p).suffix == ".bib"
        and Path(p)
        or ap.ArgumentTypeError("BIBFILE must have the extension .bib"),
        help="Converting Bibtex to CITATION.cff fileformat",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        metavar="OUTFILE",
        type=str,
        help="Output file (default: CITATION.cff)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version number and exit",
    )
    subparsers = parser.add_subparsers(
        title="subcommands", description="valid subcommands", help="additional help"
    )
    parser_add = subparsers.add_parser(
        "add",
        help="Add a new default CFF definition",
        description="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-msg",
        "--message",
        metavar="MESSAGE",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-abs",
        "--abstract",
        metavar="ABSTRACT",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-repo",
        "--repository",
        metavar="REPOSITORY",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-repo-code",
        "--repository-code",
        metavar="REPOSITORY-CODE",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-repo-artifact",
        "--repository-artifact",
        metavar="REPOSITORY-ARTIFACT",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-doi",
        "--doi",
        metavar="DOI",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-lic",
        "--license",
        metavar="LICENSE",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-date",
        "--date-released",
        metavar="DATE-RELEASED",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-month",
        "--month",
        metavar="DATE-RELEASED-MONTH",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-year",
        "--year",
        metavar="DATE-RELEASED-YEAR",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_add.add_argument(
        "-pub",
        "--publisher",
        metavar="PUBLISHER",
        type=str,
        help="Add a new default CFF definition",
    )
    parser_identifiers = subparsers.add_parser(
        "identifiers",
        help="Add identifiers to the CFF definition",
        description="Add identifiers to the CFF definition",
    )
    parser_identifiers.add_argument(
        "-type",
        "--type",
        nargs="+",
        metavar="TYPE",
        type=str,
        help="Add identifiers to the CFF definition",
    )
    parser_identifiers.add_argument(
        "-value",
        "--value",
        nargs="+",
        metavar="VALUE",
        type=str,
        help="Add identifiers to the CFF definition",
    )
    parser_identifiers.add_argument(
        "-desc",
        "--description",
        nargs="+",
        metavar="DESCRIPTION",
        type=str,
        help="Add identifiers to the CFF definition",
    )
    parser_authors = subparsers.add_parser(
        "authors",
        help="Add authors to the CFF definition",
        description="Add authors to the CFF definition",
    )
    parser_authors.add_argument(
        "-family",
        "--family-name",
        nargs="+",
        metavar="FAMILY-NAME",
        type=str,
        help="Add author(s)' family name to the CFF definition",
    )
    parser_authors.add_argument(
        "-given",
        "--given-name",
        nargs="+",
        metavar="GIVEN-NAME",
        type=str,
        help="Add author(s)' given name to the CFF definition",
    )
    parser_authors.add_argument(
        "-suffix",
        "--name-suffix",
        nargs="+",
        metavar="NAME-SUFFIX",
        type=str,
        help="Add author(s)' name suffix to the CFF definition",
    )
    parser_authors.add_argument(
        "-prefix",
        "--name-prefix",
        nargs="+",
        metavar="NAME-PREFIX",
        type=str,
        help="Add author(s)' name prefix to the CFF definition",
    )
    parser_authors.add_argument(
        "-aff",
        "--affiliation",
        nargs="+",
        metavar="AFFILIATION",
        type=str,
        help="Add author(s)' affiliation to the CFF definition",
    )
    parser_authors.add_argument(
        "-orcid",
        "--orcid",
        nargs="+",
        metavar="ORCID",
        type=str,
        help="Add author(s)' ORCID to the CFF definition",
    )
    parser_authors.add_argument(
        "-email",
        "--email",
        nargs="+",
        metavar="EMAIL",
        type=str,
        help="Add author(s)' email to the CFF definition",
    )
    return parser.parse_args()


def main() -> None:
    """Main function for bibtex2cff."""
    args = cmd()

    bibtex_path = args.bibfile
    definition = CFFDefintionUpdate(
        bibtex_path, **{k: v for k, v in vars(args).items() if v is not None}
    ).get_definition
    if args.outfile:
        save_cff_definition(definition, Path.cwd(), args.outfile)
    else:
        save_cff_definition(definition)
