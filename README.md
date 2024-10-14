# A Python client for the Publications Office of the European Union

This package provides a python wrapper to query and retrieve documents among the various endpoints of Cellar.

## Software analsysis

The program starts by sending a given SPARQL query (defining, for example, the types, the language, and the domain of the documents to retrieve) to the EU Sparql endpoint to retrieve CELLAR records. The CELLAR ids are then collected and sent to the EU CELLAR endpoint to download the corresponding `.xml` and `.html` files. The program can also check which files have already been downloaded so as to download only new files. Finally, the text of the `.xml` and `.html` files is extracted, cleaned up, and output in new text files.

EU Regulation Corpus Compiler flow

* Sends a given SPARQL query to the Virtuoso Sparql endpoint of the OP.
* Retrieves CELLAR records based on the query.
* Collects CELLAR ids from the retrieved records.
* Sends a query to the CELLAR ids to the OP REST APIs endpoint.
* Downloads corresponding .xml and .html files.
* Checks if files have already been downloaded.
* Downloads only new files.
* Extracts text from .xml and .html files.
* Cleans up the extracted text.
* Outputs the cleaned text in new text files.

Key Functionality

* Retrieving CELLAR Knowledge Graph records based on a SPARQL query
* Downloading files from the API endpoint
* Checking for existing files and downloading only new ones
* Extracting, cleaning, and outputting text from .xml and .html files

## Usage

```
pip install op_cellar
poetry add op_cellar

```

## SPARQL query

```
from op_cellar.sparql import send_sparql_query

sparql_results_table = send_sparql_query("path to the file containing sparql", "path to the desired output file")


```

 the `sparql_queries/` directory was designed to retrieve EU regulatory documents in the financial domain using EuroVoc concept ids. It can be used as a template to create new queries for other domains, languages, types of documents, etc.

## Default data directories
- The information retrieved from the SPARQL endpoint is stored by default under `sparql_query_results/query_results_<date>-<time>.json` (e.g., `sparql_query_results/query_results_query_results_20201203-145051.json`).
- The list of files already downloaded is stored by default under `in_dir_lists/in_dir_<date>-<time>.txt` (e.g., `in_dir_lists/in_dir_20201214-155143.txt`).
- The list of new CELLAR ids to send to the EU CELLAR server is stored by default under `new_cellar_ids/new_cellar_ids_<date>-<time>.txt` (e.g., `new_cellar_ids/new_cellar_ids_20201214-155143.txt`).
- The retrieved `.xml` and `.html` files are downloaded to a new directory named by default `data/cellar_files_<date>-<time>/<CELLAR_ID>/` (e.g., `data/cellar_files_20201214-155143/39ca1c1c-3091-11eb-b27b-01aa75ed71a1/`).
- The generated `.txt` files are stored by default under `data/text_files_<download_date>-<download_time>.txt` (e.g., `data/text_files_20201214-155143/`).

## File names
- The downloaded HTML files are renamed with their CELLAR id (e.g., `data/cellar_files_20201214-155143/1e4dc7cb-903d-11ea-812f-01aa75ed71a1/1e4dc7cb-903d-11ea-812f-01aa75ed71a1.html`)
- The downloaded XML files are not renamed, as a single CELLAR id may apply to several documents (e.g., `data/cellar_files_20201214-155143/39ca1c1c-3091-11eb-b27b-01aa75ed71a1/C_2020411EN.01050002.xml`)
- The generated `.txt` files are all renamed with the name of the original `.xml` or `.html` file (e.g., `data/text_files_20201214-155143/C_2020411EN.01050002.txt` or `data/text_files_20201214-155143/1e4dc7cb-903d-11ea-812f-01aa75ed71a1.txt`)

## Other useful information

 ### About the text files
- When extracting the text from XML files, footnotes are currently removed to avoid them being inserted in the middle of a sentence in the text file.
- The text from nested tables in HTML files is repeated, as shown in this example.
```
Portugal — Região Autónoma da Madeira (Autonomous Region of Madeira) — Região Autónoma dos Açores (Autonomous Region of Azores) — Municipalities
— Região Autónoma da Madeira (Autonomous Region of Madeira)
— Região Autónoma dos Açores (Autonomous Region of Azores)
— Municipalities
```
- Some CELLAR ids point to HTML files that contain URIs instead of content. The linked contents are currently not retrieved (e.g., http://publications.europa.eu/resource/cellar/d4661dab-51b2-11e7-a5ca-01aa75ed71a1)

 ### About the number of CELLAR ids and downloaded files
- The number of CELLAR ids to be downloaded might be different from the number of files actually downloaded due to the fact that a single CELLAR id can correspond to multiple `.xml` files.
- When subtracting the list of files that had been downloaded on a previous occasion (e.g., `14949`) from the list of CELLAR ids retrieved by the query (e.g., `15175`), we obtain the number of CELLAR ids to be sent to the EU CELLAR endpoint to download the corresponding files (e.g., `15175 - 14949 = 226`). However, the number thus obtained may be different from the number of actual downloads (e.g., `242`). This seems to be due to the fact that some of the pre-existing CELLAR ids are not present on the newly retrieved CELLAR id list  (e.g., `16 + 226 = 242`).


## Acknowledgements

It has been inspired by a series of previous packages and builds upon their architecture and workflows.

These are some of the sources involved:

### EU Corpus Compiler

[![DOI](https://zenodo.org/badge/202197619.svg)](https://zenodo.org/badge/latestdoi/202197619)

RegDef project are available at https://seljaseppala.wordpress.com/research/regdef/.