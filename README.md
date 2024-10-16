# op_cellar, a Python client for the CELLAR Publications Office of the European Union

**Table of Contents**

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [User Guide](#user-guide)

## 1. Introduction

The ```op_cellar``` package is a Python client that provides a wrapper to query and retrieve documents among the various endpoints of the Publications Office of the European Union. This README will guide you through its installation and usage

## 2. Installation

### 2.1 Using Poetry Dependency Manager

It is highly recommended to use Poetry as the dependency manager. To install op_cellar using Poetry, follow these steps:

1. Set up a Poetry environment by running the following command in your terminal:
```
poetry init
```
2. Add OP Cellar as a dependency in your `pyproject.toml` file by running the following command:
```
poetry add op_cellar
```

### 2.2 Using Pip

Alternatively, you can install OP Cellar using Pip by running the following command in your terminal:
```
pip install op_cellar
```

## 3. User Guide

### 3.1 SPARQL Query

To send a SPARQL query using OP Cellar, you need to import the `send_sparql_query` function from the `op_cellar.sparql` module. Here is an example:

```python
from op_cellar.sparql import send_sparql_query

sparql_results_table = send_sparql_query("path_to_sparql_file", "path_to_output_file")
```
Replace `"path_to_sparql_file"` with the actual path to your SPARQL query file and `"path_to_output_file"` with the desired output file path.

## Acknowledgements

The op_cellar package has been inspired by a series of previous packages and builds upon some of their architectures and workflows. We would like to acknowledge the following sources that have contributed to the development of this generic solution solution:

* The (eu_corpus_compiler)[https://github.com/seljaseppala/eu_corpus_compiler] package by Selja Seppala
