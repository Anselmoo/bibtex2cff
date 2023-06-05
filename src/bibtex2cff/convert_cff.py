"""Module for converting BibTeX to CFF."""
from abc import ABC
from abc import abstractmethod
from abc import abstractproperty
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Protocol
from typing import Tuple
from typing import Type

import bibtexparser as bib
import yaml

from bibtex2cff.definitions import BibTeXDefinition
from bibtex2cff.definitions import CFFDefinition
from bibtexparser.bparser import BibTexParser


class TypeDefinition(ABC):
    """Abstract class for BibTeX types."""

    def __init__(self, bib_entry: Dict[str, Any]) -> None:
        """Initialize the class with a BibTeX entry.

        Args:
            bib_entry (Dict[str, Any]): A BibTeX entry.
        """
        self.bib_entry = bib_entry

    @abstractmethod
    def __call__(self) -> Dict[str, Any]:
        """Convert the BibTeX entry to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the BibTeX entry.
        """


class SoftwareDefinition(TypeDefinition):
    """Class for BibTeX software entries."""

    def __init__(self, bib_entry: Dict[str, Any]) -> None:
        """Initialize the class with a BibTeX entry.

        Args:
            bib_entry (Dict[str, Any]): A BibTeX entry.
        """
        super().__init__(bib_entry)

    def __call__(self) -> Dict[str, Any]:
        """Convert the BibTeX entry to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the BibTeX entry.
        """
        return BibTeXDefinition(**self.bib_entry).dict(exclude_none=True)


class DatasetDefinition(TypeDefinition):
    """Class for BibTeX dataset entries."""

    def __init__(self, bib_entry: Dict[str, Any]) -> None:
        """Initialize the class with a BibTeX entry.

        In case of providing a software entry, the version field is removed.

        Args:
            bib_entry (Dict[str, Any]): A BibTeX entry.
        """
        if "version" in bib_entry:
            bib_entry.pop("version")
        super().__init__(bib_entry)

    def __call__(self) -> Dict[str, Any]:
        """Convert the BibTeX entry to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the BibTeX entry.
        """
        return BibTeXDefinition(**self.bib_entry).dict(exclude_none=True)


class BibTeXReader:
    """A class for reading BibTeX files."""

    def __init__(self, bibtex_path: str) -> None:
        """Initialize the class with a BibTeX file path.

        Args:
            bibtex_path (str): A path to a BibTeX file.
        """
        self.bibtex_path = Path(bibtex_path)

    def read_bibtex_file(self) -> Dict[str, Any]:
        """Read a BibTeX file and return the first entry.

        Returns:
            Dict[str, Any]: A dictionary representation of the BibTeX entry.
        """
        parser = BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        parser.homogenise_fields = False
        with open(file=self.bibtex_path, mode="r", encoding="utf-8") as bibtex_file:
            return bib.load(bibtex_file, parser=parser).entries[0]


class DefinitionBridge(Protocol):
    """Abstract class for CFF bridges."""

    @abstractproperty
    def get_definition(self) -> Dict[str, Any]:
        """Get the definition for the CFF file."""


class DefaultDefinition(DefinitionBridge):
    """Class for default definitions."""

    def __init__(
        self,
        cff_version: Optional[str] = None,
        license_: Optional[str] = None,
        version: Optional[str] = None,
        date_released: Optional[str] = None,
    ) -> None:
        """Initialize the class with a definition.

        According to define the initial CFF specification, the default values are:

        - cff_version: 1.2.0
        - license: Unlicense
        - version: 0.0.1
        - date_released: current date

        Args:
            cff_version (Optional[str], optional): The CFF version. Defaults to None.
            license_ (Optional[str], optional): The license. Defaults to None.
            version (Optional[str], optional): The version. Defaults to None.
            date_released (Optional[str], optional): The date released. Defaults to
                None.
        """
        self.definition = {
            "cff_version": cff_version or "1.2.0",
            "license": license_ or "Unlicense",
            "version": version or "0.0.1",
            "date_released": date_released or datetime.now().strftime("%Y-%m-%d"),
        }

    @property
    def get_definition(self) -> Dict[str, Any]:
        """Get the default definition for the CFF file.

        Returns:
            Dict[str, Any]: The default definition.
        """
        return self.definition


class OptionalDefinition(DefinitionBridge):
    """Class for optional definitions."""

    def __init__(self, _dict: Dict[str, Any], **kwargs: Dict[str, Any]) -> None:
        """Initialize the class with a definition.

        Args:
            _dict (Dict[str, Any]): A dictionary with the optional definition.
            **kwargs (Dict[str, Any]): Optional keyword arguments.
        """
        self.definition = {**_dict, **kwargs}

    @property
    def get_definition(self) -> Dict[str, Any]:
        """Get the optional definition for the CFF file.

        Returns:
            Dict[str, Any]: The updated dictionary.
        """
        return self.definition


class ImportDefinition(DefinitionBridge):
    """Class for imported BibTeX definitions."""

    def __init__(self, bibtex_path: str) -> None:
        """Initialize the class with a BibTeX file path.

        Args:
            bibtex_path (str): A path to a BibTeX file.
        """
        self.bibtex_path = bibtex_path

    @staticmethod
    def load_bibtex(bibtex_path: str) -> Tuple[str, Dict[str, Any]]:
        """Get the definition for the CFF file.

        Args:
            bibtex_path (str): The path to the BibTeX file.

        Returns:
            Tuple[str, Dict[str, Any]]: The type of the BibTeX entry and the BibTeX
                 entry.
        """
        bib_entry = BibTeXReader(bibtex_path).read_bibtex_file()
        return bib_entry["ENTRYTYPE"], bib_entry

    @property
    def get_definition(self) -> Dict[str, Any]:
        """Get the definition for a given language.

        Returns:
            Dict[str, Any]: A dictionary representation of the BibTeX entry.
        """
        _type, kwargs = self.load_bibtex(self.bibtex_path)
        definitions: Dict[str, Type[TypeDefinition]] = {
            "software": SoftwareDefinition,
            "datatset": DatasetDefinition,
            "misc": DatasetDefinition,
        }
        return definitions[_type](kwargs)()


class CFFDefinitionUpdate(DefinitionBridge):
    """Class for updating CFF definitions."""

    def __init__(self, bibtex_path: str, **kwargs: Dict[str, Any]) -> None:
        """Initialize the class with default, BibTeX, and optional definitions.

        Args:
            bibtex_path (str): The path to the BibTeX file.
            **kwargs (Dict[str, Any]): Optional keyword arguments.
        """
        self.default = DefaultDefinition
        self.bibtex = ImportDefinition
        self.optional = OptionalDefinition

        self.bibtex_path = bibtex_path
        self.kwargs = kwargs

    @property
    def get_definition(self) -> Dict[str, Any]:
        """Get the definition for a given language.

        Returns:
            Dict[str, Any]: A dictionary representation of the CFF entry.
        """
        definition = self.default().get_definition
        definition.update(self.bibtex(self.bibtex_path).get_definition)
        definition.update(self.optional(definition, **self.kwargs).get_definition)
        return self.replace_hyphens_with_underscores(
            CFFDefinition(**definition).dict(exclude_none=True, by_alias=True)
        )

    def replace_hyphens_with_underscores(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace hyphens with underscores in a dictionary.

        Args:

            data (Dict[str, Any]): A dictionary.

        Returns:
            Dict[str, Any]: A dictionary with hyphens replaced with underscores.
        """
        if isinstance(data, dict):
            return {
                k.replace("_", "-"): self.replace_hyphens_with_underscores(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self.replace_hyphens_with_underscores(v) for v in data]
        else:
            return data


def save_cff_definition(
    cff_definition: Dict[str, Any],
    directory: Optional[Path] = None,
    citation_cff: str = "CITATION.cff",
) -> None:
    """Save a CFFDefinition object as a YAML file.

    Save a CFFDefinition object as a YAML file named CITATION.cff in the
    specified directory. If the file already exists, it will be overwritten.

    Args:
        cff_definition (Dict[str, Any]): A dictionary representation of the CFF
             entry.
        directory (Path): The directory to save the file in.
        citation_cff (str, optional): The name of the file to save. Defaults to
             "CITATION.cff".

    """
    directory = directory or Path.cwd()
    with open(directory / citation_cff, "w", encoding="utf-8") as file:
        yaml.dump(cff_definition, file, allow_unicode=True, sort_keys=False, indent=2)
