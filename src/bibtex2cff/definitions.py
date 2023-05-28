"""Definitions for the CFF and BibTeX formats."""
import re

from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import validator


class AuthorDefinition(BaseModel):
    """Class for author definitions."""

    given_name: Optional[str] = Field(
        default=None, min_length=1, description="Given name of the author, optional."
    )
    name_particle: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Name particle of the author, optional.",
    )
    family_name: str = Field(
        ...,
        min_length=1,
        description="Family name of the author, required.",
    )
    name_suffix: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Name suffix of the author, optional.",
    )
    orcid: Optional[HttpUrl] = Field(
        default=None,
        description="ORCID of the author, optional.",
    )
    affiliation: Optional[str] = Field(
        default=None,
        description="Affiliation of the author, optional.",
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Email of the author, optional.",
    )


class IdentifierDefinition(BaseModel):
    """Class for identifier definitions."""

    type_: Optional[str] = Field(
        default=None,
        description="Type of the identifier, which can be one of the following:"
        " doi, url, swh",
        alias="type",
    )
    value: Optional[str] = Field(
        default=None,
        description="Value of the identifier, which can be one of the following:"
        " doi, url, swh",
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the identifier, optional.",
    )


class CFFDefinition(BaseModel):
    """Class for CFF definitions."""

    cff_version: str = Field(
        ...,
        description="The version of the CFF format used in this file.",
        regex=r"^1\.2\.\d$",
    )
    title: str = Field(
        ...,
        description="The title of the software or other project.",
        min_length=1,
    )
    message: str = Field(
        default="If you use this software, please cite it as below.",
        description="A short description of the software or other project.",
        min_length=1,
    )
    abstract: Optional[str] = Field(
        default=None,
        description="A longer description of the software or other project.",
        min_length=1,
    )
    author: List[AuthorDefinition] = Field(
        ...,
        description="A list of authors of the software or other project.",
        min_items=1,
    )
    identifiers: Optional[List[IdentifierDefinition]] = Field(
        default=None,
        description="A list of identifiers for the software or other project.",
        min_items=1,
    )
    doi: str = Field(
        ...,
        description="The DOI of the software or other project.",
        min_length=1,
    )
    url: str = Field(
        ...,
        description="The URL of the landing page of the software or other project.",
    )
    repository: Optional[str] = Field(
        default=None,
        description="The URL of the repository where the source code of the software or"
        " other project is hosted.",
    )
    repository_code: Optional[str] = Field(
        default=None,
        description="The URL of the repository where the source code of the software or"
        " other project is hosted.",
    )
    repository_artifact: Optional[str] = Field(
        default=None,
        description="The URL of the repository where the source code of the software or"
        " other project is hosted.",
    )
    license_: str = Field(
        ...,
        description="The license of the software or other project.",
        min_length=1,
        alias="license",
    )
    keywords: Optional[List[str]] = Field(
        default=None,
        description="A list of keywords for the software or other project.",
        min_items=1,
    )
    version: str = Field(
        ...,
        description="The version of the software or other project.",
        min_length=1,
    )
    commit: Optional[str] = Field(
        default=None,
        description="The commit hash of the software or other project.",
        min_length=1,
        regex=r"^[a-f0-9]{40}$",
    )
    date_released: str = Field(
        ...,
        description="The date the software or other project was released.",
        regex=r"^\d{4}-\d{2}-\d{2}$",
    )

    @validator("url", "repository", "repository_artifact", "repository_code", pre=True)
    @classmethod
    def url_transform(cls, v: HttpUrl) -> str:
        """Transform the URL to a string.

        Args:
            v (HttpUrl): URL.

        Raises:
            ValueError: If the URL is not valid.

        Returns:
            str: URL as a string.
        """
        return str(v)

    @validator("license_", pre=True)
    @classmethod
    def license_validate(cls, v: str) -> str:
        """Validate the license acronym.

        Args:
            v (str): License acronym.

        Raises:
            ValueError: If the license acronym is not valid.

        Returns:
            str: License acronym.
        """
        valid_licenses = [
            "AGPL-3.0-or-later",
            "Apache-2.0",
            "BSD-2-Clause",
            "BSD-3-Clause",
            "CC-BY-4.0",
            "CC-BY-SA-4.0",
            "CC0-1.0",
            "EPL-2.0",
            "GPL-2.0-or-later",
            "GPL-3.0-or-later",
            "ISC",
            "LGPL-2.1-or-later",
            "LGPL-3.0-or-later",
            "MIT",
            "MPL-2.0",
            "Unlicense",
        ]

        if v not in valid_licenses:
            raise ValueError(
                f"License {v} is not valid. Please use one of the "
                f"following: {valid_licenses}"
            )
        return v


class ABCSplit(ABC):
    """Abstract base class for splitting strings."""

    @abstractmethod
    def transform(self) -> Union[List[str], AuthorDefinition, List[AuthorDefinition]]:
        """Abstract method for splitting strings.

        Returns:
            Union[List[str], AuthorDefinition, List[AuthorDefinition]]: List of strings.
        """


class AndSplit(ABCSplit):
    """Split the string at the " and " and return the list."""

    def __init__(self, x: str) -> None:
        """Initialize the class.

        Args:
            x (str): String to split.
        """
        self.x = x

    def transform(self) -> List[str]:
        """Split the string at the " and " and return the list.

        Returns:
            List[str]: List of authors names split at the " and ".
        """
        return [x.strip() for x in re.split(r" and ", self.x, flags=re.IGNORECASE)]


class NameSplit(ABCSplit):
    """Split the string by comma and return an AuthorDefinition object."""

    def __init__(self, x: str):
        """Initialize the class.

        Args:
            x (str): String to split.
        """
        self.x = x

    def split_by_comma(self) -> AuthorDefinition:
        """Split the string by comma and return an AuthorDefinition object.

        Returns:
            AuthorDefinition: AuthorDefinition object.
        """
        name_list = self.x.split(",")
        if len(name_list[1].split(" ")) > 2:
            return AuthorDefinition(
                given_name=name_list[1].split(" ")[1].strip(),
                family_name=name_list[0].strip(),
                name_suffix=name_list[1].split(" ")[2].strip(),
            )
        return AuthorDefinition(
            given_name=name_list[1].strip(),
            family_name=name_list[0].strip(),
        )

    def split_by_space(self) -> AuthorDefinition:
        """Split the string by space and return an AuthorDefinition object.

        Returns:
            AuthorDefinition: AuthorDefinition object.
        """
        parts = self.x.split()
        return AuthorDefinition(
            given_name=parts[0].strip() if len(parts) > 1 else None,
            family_name=parts[-1].strip(),
            name_suffix=parts[1].strip() if len(parts) == 3 else None,
        )

    def transform(self) -> AuthorDefinition:
        """Split the string by comma and return an AuthorDefinition object.

        Returns:
            AuthorDefinition: AuthorDefinition object.
        """
        return self.split_by_comma() if "," in self.x else self.split_by_space()


class AuthorConvert(ABCSplit):
    """Convert a string to a list of AuthorDefinition objects."""

    def __init__(self, x: str):
        """Initialize the class.

        Args:
            x (str): String to split.
        """
        self.x = x

    def transform(self) -> List[AuthorDefinition]:
        """Transform the string to a list of AuthorDefinition objects.

        Split the string by " and " or comma and space and return a list of
        AuthorDefinition objects.

        Returns:
            List[AuthorDefinition]: List of AuthorDefinition objects.
        """
        return [
            NameSplit(x=author).transform() for author in AndSplit(x=self.x).transform()
        ]

    def __call__(self) -> List[AuthorDefinition]:
        """Call the transform method.

        Returns:
            List[AuthorDefinition]: List of AuthorDefinition objects.
        """
        return self.transform()


class BibTeXDefinition(BaseModel):
    """BibTeX definition."""

    author: List[AuthorDefinition] = Field(
        ..., description="The author(s) of the software or other project."
    )

    title: str = Field(
        ...,
        description="The title of the software or other project.",
        min_length=1,
    )
    month: str = Field(
        ...,
        description="The month the software or other project was released.",
        min_length=1,
        regex=r"^[A-Za-z]+$",
    )
    year: int = Field(
        ...,
        description="The year the software or other project was released.",
        ge=1800,
    )
    publisher: str = Field(
        ...,
        description="The publisher of the software or other project.",
        min_length=1,
    )
    url: HttpUrl = Field(
        ...,
        description="The URL of the landing page of the software or other project.",
    )
    doi: str = Field(
        ...,
        description="The DOI of the software or other project.",
        min_length=1,
    )
    version: Optional[str] = Field(
        default=None,
        description="The version of the software or other project.",
        min_length=1,
    )

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    @validator("author", pre=True)
    @classmethod
    def author_validate(cls, v: str) -> List[AuthorDefinition]:
        """Validate the author field.

        Args:
            v (str): The author field.

        Raises:
            ValueError: If the author field is not valid.

        Returns:
            List[AuthorDefinition]: List of AuthorDefinition objects.
        """
        return AuthorConvert(x=v)()
