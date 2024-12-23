Getting Started
===============

Installation
------------

To use tulit, first install it using poetry:

.. code-block:: console

    $ poetry shell
    $ poetry install

Then, you can import it in your Python code:

Basic Usage
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

To parse a Formex document, you can use the ``Formex4Parser`` class. Below is an example of how to use it:

.. code-block:: python

    from tulit.parsers.formex import Formex4Parser

    # Initialize the parser
    parser = Formex4Parser()

    # Path to the Formex XML file
    file_path = 'path/to/your/formex.xml'

    # Parse the file
    parsed_data = parser.parse(file_path)

    # Access parsed data
    print(parsed_data)
