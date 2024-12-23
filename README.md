# `tulit`, The Universal Legal Informatics Toolkit

[![Publish Package to PyPI](https://github.com/AlessioNar/op_cellar/actions/workflows/publish.yml/badge.svg)](https://github.com/AlessioNar/op_cellar/actions/workflows/publish.yml)

## 1. Introduction

The `tulit` package provides utilities to work with legal data in a way that legal informatics practitioners can focus on addding value. 

## 2. Installation

### 2.1 Using Poetry Dependency Manager
It is highly recommended to use Poetry as a dependency manager. To install the `tulit` package using Poetry, follow these steps:

1. Set up a Poetry environment by running the following command in your terminal:

```
poetry init
poetry shell
```


2. Add the `tulit` package as a dependency in your `pyproject.toml` file by running the following command:

```
poetry add tulit
```

### 2.2 Using Pip

Alternatively, you can install the `tulit` package in the environment of your choice by using pip by running the following command in your terminal:

```
pip install tulit
```

## Acknowledgements

The `tulit` package has been inspired by a series of previous packages and builds upon some of their architectures and workflows. We would like to acknowledge the following sources that have contributed to the ideation of the `tulit` package:

* The [eu_corpus_compiler](https://github.com/seljaseppala/eu_corpus_compiler) repository by Selja Seppala concerning the methods used to query the CELLAR SPARQL API and WEB APIs
* The implementation of the Akoma Ntoso parser made in the [SORTIS project repository](https://code.europa.eu/regulatory-reporting/sortis)

* [EURLEX package by step 21](https://github.com/step21/eurlex)
* [the eurlex package by kevin91nl](https://github.com/kevin91nl/eurlex/)
* [the eurlex2lexparency package](https://github.com/Lexparency/eurlex2lexparency)
* [the extraction_libraries by the Maastricht Law and Tech Lab](https://github.com/maastrichtlawtech/extraction_libraries)
* [the closer library by the Maastricht Law and Tech Lab](https://github.com/maastrichtlawtech/closer)

### Use of existing standards and structured formats

* [LegalDocML (Akoma Ntoso)](https://groups.oasis-open.org/communities/tc-community-home2?CommunityKey=3425f20f-b704-4076-9fab-018dc7d3efbe)
* [LegalHTML](https://art.uniroma2.it/legalhtml/)
* [FORMEX](https://op.europa.eu/documents/3938058/5910419/formex_manual_on_screen_version.html)

