"""Tests for the convert_cff module."""

from datetime import datetime
from pathlib import Path

import pytest
import yaml

from bibtex2cff.convert_cff import BibTeXReader
from bibtex2cff.convert_cff import CFFDefintionUpdate
from bibtex2cff.convert_cff import DatasetDefinition
from bibtex2cff.convert_cff import DefaultDefinition
from bibtex2cff.convert_cff import ImportDefinition
from bibtex2cff.convert_cff import OptionalDefinition
from bibtex2cff.convert_cff import SoftwareDefinition
from bibtex2cff.convert_cff import save_cff_definition
from bibtex2cff.definitions import AuthorDefinition
from bibtex2cff.definitions import CFFDefinition
from pydantic import BaseModel
from pydantic import HttpUrl


def test_dataset_definition() -> None:
    assert DatasetDefinition(
        dict(
            author="John Doe",
            title="My Software",
            month="jan",
            year=2010,
            publisher="My Publisher",
            url="https://example.com",
            doi="10.1234/5678",
            version="1.0.0",
        )
    )() == dict(
        author=[
            AuthorDefinition(given_name="John", family_name="Doe").dict(
                exclude_none=True
            )
        ],
        title="My Software",
        month="jan",
        year=2010,
        publisher="My Publisher",
        url="https://example.com",
        doi="10.1234/5678",
    )


def test_software_definition() -> None:
    """Test the SoftwareDefinition class."""
    assert SoftwareDefinition(
        dict(
            author="John Doe and Jane Smith",
            title="My Software",
            month="jan",
            year=2010,
            publisher="My Publisher",
            url="https://example.com",
            doi="10.1234/5678",
            version="1.0.0",
        )
    )() == dict(
        author=[
            AuthorDefinition(given_name="John", family_name="Doe").dict(
                exclude_none=True
            ),
            AuthorDefinition(given_name="Jane", family_name="Smith").dict(
                exclude_none=True
            ),
        ],
        title="My Software",
        month="jan",
        year=2010,
        publisher="My Publisher",
        url="https://example.com",
        doi="10.1234/5678",
        version="1.0.0",
    )


def test_default_definition() -> None:
    """Test the DefaultDefinition class."""
    assert DefaultDefinition().get_definition == dict(
        cff_version="1.2.0",
        license="Unlicense",
        version="0.0.1",
        date_released=datetime.now().strftime("%Y-%m-%d"),
    )


@pytest.fixture
def bibtex_file(tmp_path: Path) -> Path:
    """Create a temporary BibTeX file."""
    bibtex_path = tmp_path / "test.bib"
    bibtex_path.write_text(
        """
        @misc{test,
            title = {Test Title},
            author = {Test Author},
            year = {2022},
            month = jan,
            publisher = {Test Publisher},
            url = {https://example.com},
            doi = {10.1234/5678},
        }
        """
    )
    return bibtex_path


def test_import_definition(bibtex_file: Path) -> None:
    """Test the import definition."""
    definition = ImportDefinition(str(bibtex_file)).get_definition

    class ExampleUrl(BaseModel):
        """Example URL."""

        url: HttpUrl = "https://example.com"  # type: ignore

    assert definition["author"] == [{"family_name": "Author", "given_name": "Test"}]
    assert definition["doi"] == "10.1234/5678"
    assert definition["month"] == "January"
    assert definition["publisher"] == "Test Publisher"
    assert definition["title"] == "Test Title"
    assert definition["url"] == ExampleUrl().url
    assert definition["year"] == 2022


def test_BibTeX_reader(bibtex_file: Path) -> None:
    """Test the BibTeX reader."""
    reader = BibTeXReader(str(bibtex_file))
    definition = reader.read_bibtex_file()

    assert definition["author"] == "Test Author"
    assert definition["doi"] == "10.1234/5678"
    assert definition["month"] == "January"
    assert definition["publisher"] == "Test Publisher"
    assert definition["title"] == "Test Title"
    assert definition["url"] == "https://example.com"
    assert definition["year"] == "2022"


def test_optional_definition() -> None:
    """Test the optional definition."""
    definition = OptionalDefinition(
        {"author": "John Doe", "title": "My Software", "month": "jan"},
        year=2010,  # type: ignore
        publisher="My Publisher",  # type: ignore
        url="https://example.com",  # type: ignore
        doi="10.1234/5678",  # type: ignore
    ).get_definition
    assert definition["author"] == "John Doe"
    assert definition["title"] == "My Software"
    assert definition["month"] == "jan"
    assert definition["year"] == 2010
    assert definition["publisher"] == "My Publisher"
    assert definition["url"] == "https://example.com"
    assert definition["doi"] == "10.1234/5678"


def test_cff_definition_update(bibtex_file: Path) -> None:
    """Test the CFF definition update."""
    definition = CFFDefintionUpdate(
        str(bibtex_file),
        repository="https://repo.example.com",  # type: ignore
    ).get_definition
    assert definition["author"] == [{"family_name": "Author", "given_name": "Test"}]
    assert definition["doi"] == "10.1234/5678"
    assert definition["repository"] == "https://repo.example.com"


def test_save_cff_definition(tmp_path: Path) -> None:
    """Test the save_cff_definition function."""

    cff_definition = CFFDefinition(
        cff_version="1.2.0",
        message="Test message",
        author=[
            AuthorDefinition(given_name="John", family_name="Doe"),
            AuthorDefinition(given_name="Jane", family_name="Smith"),
        ],
        title="My Software",
        doi="10.1234/5678",
        url="https://example.com",
        version="1.0.0",
        license="MIT",
        date_released=datetime.now().strftime("%Y-%m-%d"),
    ).dict(exclude_none=True)
    save_cff_definition(
        cff_definition=cff_definition, directory=tmp_path, citation_cff="test.cff"
    )
    assert (tmp_path / "test.cff").exists()

    with open(tmp_path / "test.cff", "r", encoding="utf-8") as f:
        cff_definition = yaml.safe_load(f)

    assert cff_definition["title"] == "My Software"
    assert cff_definition["doi"] == "10.1234/5678"
    assert cff_definition["version"] == "1.0.0"
