"""Test the definitions module."""
from bibtex2cff.definitions import AndSplit
from bibtex2cff.definitions import AuthorConvert
from bibtex2cff.definitions import AuthorDefinition
from bibtex2cff.definitions import BibTeXDefinition
from bibtex2cff.definitions import NameSplit
from pydantic import BaseModel
from pydantic import HttpUrl


class TestNameSplit:
    """Test the NameSplit class."""

    def test_split_by_comma_0(self) -> None:
        """Test splitting by comma."""
        name_split = NameSplit("Doe, John")
        author_definition = name_split.transform()
        assert author_definition.given_name == "John"
        assert author_definition.family_name == "Doe"
        assert author_definition.name_suffix is None

        name_split = NameSplit("Doe,John")
        author_definition = name_split.transform()
        assert author_definition.given_name == "John"
        assert author_definition.family_name == "Doe"
        assert author_definition.name_suffix is None

    def test_split_by_comma_1(self) -> None:
        """Test splitting by comma with name suffix."""
        name_split = NameSplit("Doe, John Jr.")
        author_definition = name_split.transform()
        assert author_definition.given_name == "John"
        assert author_definition.family_name == "Doe"
        assert author_definition.name_suffix == "Jr."

        name_split = NameSplit("Doe, John Jr. ")
        author_definition = name_split.transform()
        assert author_definition.given_name == "John"
        assert author_definition.family_name == "Doe"
        assert author_definition.name_suffix == "Jr."

    def test_split_by_space_0(self) -> None:
        """Test splitting by space."""
        name_split = NameSplit("Doe")
        author_definition = name_split.transform()
        assert author_definition.given_name is None
        assert author_definition.family_name == "Doe"
        assert author_definition.name_suffix is None

    def test_split_by_space_1(self) -> None:
        """Test splitting by space."""
        name_split = NameSplit("John Doe")
        author_definition = name_split.transform()
        assert author_definition.given_name == "John"
        assert author_definition.family_name == "Doe"
        assert author_definition.name_suffix is None
        name_split = NameSplit("John Doe ")
        author_definition = name_split.transform()
        assert author_definition.given_name == "John"
        assert author_definition.family_name == "Doe"
        assert author_definition.name_suffix is None

    def test_split_by_space_2(self) -> None:
        """Test splitting by space with name suffix."""
        name_split = NameSplit("John Jr. Doe ")
        author_definition = name_split.transform()
        assert author_definition.given_name == "John"
        assert author_definition.family_name == "Doe"
        assert author_definition.name_suffix == "Jr."
        name_split = NameSplit("John Jr. Doe")
        author_definition = name_split.transform()
        assert author_definition.given_name == "John"
        assert author_definition.family_name == "Doe"
        assert author_definition.name_suffix == "Jr."


class TestAndSplit:
    """Test the AndSplit class."""

    def test_transform(self) -> None:
        """Test the transform method."""
        # Test case 1: Test with one author name
        and_split = AndSplit("John Doe")
        assert and_split.transform() == ["John Doe"]

        # Test case 2: Test with two author names separated by "and"
        and_split = AndSplit("John Doe and Jane Smith")
        assert and_split.transform() == ["John Doe", "Jane Smith"]

        # Test case 3: Test with two author names separated by "And"
        and_split = AndSplit("John Doe And Jane Smith")
        assert and_split.transform() == ["John Doe", "Jane Smith"]

        # Test case 4: Test with three author names separated by "and"
        and_split = AndSplit("John Doe and Jane Smith and Bob Johnson")
        assert and_split.transform() == ["John Doe", "Jane Smith", "Bob Johnson"]

        # Test case 5: Test with three author names separated by "And"
        and_split = AndSplit("John Doe And Jane Smith And Bob Johnson")
        assert and_split.transform() == ["John Doe", "Jane Smith", "Bob Johnson"]


class TestAuthorConvert:
    """Test the AuthorConvert class."""

    def test_single_author_given_name_family_name(self) -> None:
        """Test with a single author with given name and family name."""
        input_str = "John Doe"
        expected_output = [AuthorDefinition(given_name="John", family_name="Doe")]
        assert AuthorConvert(input_str).transform() == expected_output

    def test_single_author_family_name_only(self) -> None:
        """Test with a single author with family name only."""
        input_str = "Doe"
        expected_output = [AuthorDefinition(family_name="Doe")]
        assert AuthorConvert(input_str).transform() == expected_output

    def test_multiple_authors_and_separator(self) -> None:
        """Test with multiple authors separated by and."""
        input_str = "John Doe and Jane Smith"
        expected_output = [
            AuthorDefinition(given_name="John", family_name="Doe"),
            AuthorDefinition(given_name="Jane", family_name="Smith"),
        ]
        assert AuthorConvert(input_str).transform() == expected_output

    def test_multiple_authors_comma_space_separator(self) -> None:
        """Test with multiple authors separated by comma and space."""
        input_str = "Doe, John and Smith, Jane"
        expected_output = [
            AuthorDefinition(given_name="John", family_name="Doe"),
            AuthorDefinition(given_name="Jane", family_name="Smith"),
        ]
        assert AuthorConvert(input_str).transform() == expected_output

    def test_multiple_authors_comma_separator(self) -> None:
        """Test with multiple authors separated by comma."""
        input_str = "Doe, John Jr. and  Smith, Jane M."
        expected_output = [
            AuthorDefinition(given_name="John", family_name="Doe", name_suffix="Jr."),
            AuthorDefinition(given_name="Jane", family_name="Smith", name_suffix="M."),
        ]
        assert AuthorConvert(input_str).transform() == expected_output

    def test_multiple_authors_and_comma_separator(self) -> None:
        """Test with multiple authors separated by and and comma."""
        input_str = "John Jr. Doe and Jane M. Smith"
        expected_output = [
            AuthorDefinition(given_name="John", family_name="Doe", name_suffix="Jr."),
            AuthorDefinition(given_name="Jane", family_name="Smith", name_suffix="M."),
        ]
        assert AuthorConvert(input_str).transform() == expected_output


def test_bibtex_definition() -> None:
    """Test the BibTeXDefinition class."""
    author = "John Doe"
    title = "My Project"
    month = "January"
    year = 2022
    publisher = "My Publisher"
    doi = "10.1234/example"
    version = "1.0.0"

    class ExampleUrl(BaseModel):
        """Example URL."""

        url: HttpUrl = "https://example.com"  # type: ignore

    bibtex_def = BibTeXDefinition(
        author=author,  # type: ignore
        title=title,
        month=month,
        year=year,
        publisher=publisher,
        url="https://example.com",  # type: ignore
        doi=doi,
        version=version,
    )

    assert bibtex_def.author == [AuthorDefinition(given_name="John", family_name="Doe")]
    assert bibtex_def.title == title
    assert bibtex_def.month == month
    assert bibtex_def.year == year
    assert bibtex_def.publisher == publisher
    assert bibtex_def.url == ExampleUrl().url
    assert bibtex_def.doi == doi
    assert bibtex_def.version == version
