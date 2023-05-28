"""Test the command line interface."""
from pathlib import Path

# from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from bibtex2cff.cmd import cmd


# from bibtex2cff.cmd import main


@pytest.fixture
def bib_file(tmp_path: Path) -> str:
    bib_str = """@misc{dataset_2022_6800385,
      author       = {DATASET},
      title        = {Dataset of code metrics},
      month        = jul,
      year         = 2022,
      publisher    = {Zenodo},
      doi          = {10.5281/zenodo.6800385},
      url          = {https://doi.org/10.5281/zenodo.6800385}
    }"""

    bib_file = tmp_path / "test.bib"
    bib_file.write_text(bib_str)
    return str(bib_file)


def test_cmd(bib_file: str) -> None:
    """Test the command line interface."""
    with patch("sys.argv", ["bibtex2cff", bib_file]):
        cmd()
