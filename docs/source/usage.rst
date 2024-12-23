Usage
=====

.. _installation:

Installation
------------

To use tulit, first install it using poetry:

.. code-block:: console

   (.venv) $ poetry shell
   (.venv) $ poetry install

Then, you can import it in your Python code:

Usage Notes
-----------

To parse an Akoma Ntoso document, you can use the ``AkomaNtosoParser`` class. Below is an example of how to use it:

.. code-block:: python

    from tulit.parsers.akomantoso import AkomaNtosoParser

    # Initialize the parser
    parser = AkomaNtosoParser()

    # Path to the Akoma Ntoso XML file
    file_path = 'path/to/your/akomantoso.xml'

    # Parse the file
    provisions = parser.parse(file_path)

    # Access parsed data
    print(provisions)

The `AkomaNtosoParser` class provides several methods to extract different parts of the document:

- `get_meta()`: Extracts metadata from the document.
- `get_preface()`: Extracts the preface section.
- `get_preamble()`: Extracts the preamble section.
- `get_act()`: Extracts the act element.
- `get_body()`: Extracts the body element.
- `get_chapters()`: Extracts chapter information.
- `get_articles()`: Extracts article information.
- `get_conclusions()`: Extracts conclusions information.

Each method processes specific parts of the Akoma Ntoso document and stores the extracted information in the parser's attributes.

For more detailed information on each method, refer to the class documentation.
