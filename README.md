# BibTeX2CFF

[![PyPI](https://img.shields.io/pypi/v/bibtex2cff?logo=pypi&logoColor=yellow)](https://pypi.org/project/bibtex2cff/)
[![DOI](https://zenodo.org/badge/642463530.svg)](https://zenodo.org/badge/latestdoi/642463530)


## Description

This is a simple CMD-tool to convert BibTeX files to CFF files. It is dedicated to the [Citation File Format](https://citation-file-format.github.io/), which is a YAML-based format for bibliographic metadata.

The idea is faster to generate CFF files from BibTeX files, which can be used in other tools, such as [Zenodo](https://zenodo.org/).


## Installation

```bash
pip install bibtex2cff
```

## Usage

```bash
bibtex2cff <input.bib> -o <output.cff>
```


## Development

### Installation

```bash
git clone
cd bibtex2cff
poetry install --all-extras --with dev
```

### Testing

```bash
poetry run pytest
```

### Linting

```bash
poetry run flake8
poetry run black .
poetry run isort .
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

### License

This project is licensed under the terms of the [MIT license](LICENSE).
```
