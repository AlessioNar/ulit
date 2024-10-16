# `op_cellar`, a Python package for the CELLAR Publications Office of the European Union

## 1. Introduction

The `op_cellar` package is a Python client that provides a wrapper to query and retrieve documents among the various endpoints of the Publications Office of the European Union.

## 2. Installation

### 2.1 Using Poetry Dependency Manager

It is highly recommended to use Poetry as a dependency manager. To install the `op_cellar` package using Poetry, follow these steps:

1. Set up a Poetry environment by running the following command in your terminal:

```
poetry init
poetry shell
```

2. Add the `op_cellar` package as a dependency in your `pyproject.toml` file by running the following command:

```
poetry add op_cellar
```

### 2.2 Using Pip

Alternatively, you can install the `op_cellar` package in the environment of your choice by using pip by running the following command in your terminal:

```
pip install op_cellar
```

## 3. User Guide

### 3.1 SPARQL Query

To send a SPARQL query to the Publications Office SPARQL endpoint, you need to import the `send_sparql_query` function from the `op_cellar.sparql` module. Here is an example:

```python
from op_cellar.sparql import send_sparql_query

sparql_results_table = send_sparql_query("path_to_sparql_file", "path_to_output_file")
```

Replace `"path_to_sparql_file"` with the actual path to your SPARQL query file and `"path_to_output_file"` with the desired output file path for the results table.

## Acknowledgements

The op_cellar package has been inspired by a series of previous packages and builds upon some of their architectures and workflows. We would like to acknowledge the following sources that have contributed to the development of this generic solution:

* The [eu_corpus_compiler](https://github.com/seljaseppala/eu_corpus_compiler) package by Selja Seppala

## Copyright

In order to ensure the compatibility with other pre-existing software, the license of choice is the EUPL 1.2