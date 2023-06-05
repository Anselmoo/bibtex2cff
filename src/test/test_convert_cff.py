"""Tests for the convert_cff module."""

from datetime import datetime
from pathlib import Path

import pytest
import yaml

from bibtex2cff.convert_cff import BibTeXReader
from bibtex2cff.convert_cff import CFFDefinitionUpdate
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
    definition = CFFDefinitionUpdate(
        str(bibtex_file),
        repository="https://repo.example.com",  # type: ignore
    ).get_definition
    assert definition["author"] == [{"family-name": "Author", "given-name": "Test"}]
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


@pytest.fixture
def bibtex_file_mona_lisa(tmp_path: Path) -> Path:
    """Create a temporary BibTeX file."""
    bibtex_path = tmp_path / "test.bib"
    bibtex_path.write_text(
        """
        @software{Lisa_My_Research_Software_2017,
        author = {Lisa, Mona and Bot, Hew},
        doi = {10.5281/zenodo.1234},
        month = {dec},
        title = {{My Research Software}},
        url = {https://github.com/github-linguist/linguist},
        version = {2.0.4},
        year = {2017},
        publisher = {Reference},
        }
        """
    )
    return bibtex_path


def test_mona_lisa(bibtex_file_mona_lisa: Path) -> None:
    """Test the Mona Lisa example."""
    definition = CFFDefinitionUpdate(
        str(bibtex_file_mona_lisa),
        repository="https://docs.github.com/en/repositories"  # type: ignore
        "/managing-your-repositorys-settings-and-features/customizing-your-repository"
        "/about-citation-files",
    ).get_definition
    assert definition["author"] == [
        {"family-name": "Lisa", "given-name": "Mona"},
        {"family-name": "Bot", "given-name": "Hew"},
    ]
    assert definition["doi"] == "10.5281/zenodo.1234"
    assert (
        definition["repository"] == "https://docs.github.com/en/repositories/"
        "managing-your-repositorys-settings-and-features/customizing-your-repository"
        "/about-citation-files"
    )
    assert definition["version"] == "2.0.4"
    assert definition["title"] == "{My Research Software}"
    assert definition["url"] == "https://github.com/github-linguist/linguist"
