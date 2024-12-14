# `ulit`, The Universal Legal Informatics Toolkit

[![Publish Package to PyPI](https://github.com/AlessioNar/op_cellar/actions/workflows/publish.yml/badge.svg)](https://github.com/AlessioNar/op_cellar/actions/workflows/publish.yml)

## 1. Introduction

The `ulit` package provides utilities to work with legal data in a way that legal informatics practitioners can focus on addding value. 

## 2. Installation

### 2.1 Using Poetry Dependency Manager
It is highly recommended to use Poetry as a dependency manager. To install the `ulit` package using Poetry, follow these steps:

1. Set up a Poetry environment by running the following command in your terminal:

```
poetry init
poetry shell
```


2. Add the `ulit` package as a dependency in your `pyproject.toml` file by running the following command:

```
poetry add ulit
```

### 2.2 Using Pip

Alternatively, you can install the `ulit` package in the environment of your choice by using pip by running the following command in your terminal:

```
pip install ulit
```

## 3. User Guide

### 3.1 SPARQL Query

SPARQL metadata retrieval is currently supported only from the Publications Office SPARQL endpoint based on the CELEX identifier.

```python
from ulit.sparql import send_sparql_query

response = send_sparql_query(sparql_query_filepath, celex=None)
```

Replace `"sparql_query_filepath"` with the actual path to your SPARQL query file and `"celex"` with the desired celex identifier.

### 3.2 Downloading the documents

```python
from ulit.download import download_documents

download_documents(results=response, download_dir='desired_downloadpath', log_dir='desired_log_dir'format='xhtml')

```

## Acknowledgements

The ulit package has been inspired by a series of previous packages and builds upon some of their architectures and workflows. We would like to acknowledge the following sources that have contributed to the development of this generic solution:

### Integration of part of the codebase

* The [eu_corpus_compiler](https://github.com/seljaseppala/eu_corpus_compiler) repository by Selja Seppala concerning the methods used to query the CELLAR SPARQL API and WEB APIs
* The implementation of the Akoma Ntoso parser made in the [SORTIS project repository](https://code.europa.eu/regulatory-reporting/sortis)

### Inspiration in the parsing strategy

* [EURLEX package by step 21](https://github.com/step21/eurlex)
* https://github.com/kevin91nl/eurlex/
* https://github.com/Lexparency/eurlex2lexparency
* https://github.com/maastrichtlawtech/extraction_libraries
* https://github.com/maastrichtlawtech/closer

### Use of existing standards and structured formats

* [LegalDocML (Akoma Ntoso)](https://groups.oasis-open.org/communities/tc-community-home2?CommunityKey=3425f20f-b704-4076-9fab-018dc7d3efbe)
* [LegalHTML](https://art.uniroma2.it/legalhtml/)
* [FORMEX](https://op.europa.eu/documents/3938058/5910419/formex_manual_on_screen_version.html)

