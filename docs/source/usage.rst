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
----------------

To parse an Akoma Ntoso document, you can use the ``AkomaNtosoParser`` class:

.. autofunction:: AkomaNtosoParser()

The ``kind`` parameter should be either ``"meat"``, ``"fish"``,
or ``"veggies"``. Otherwise, :py:func:`lumache.get_random_ingredients`
will raise an exception.

.. autoexception:: lumache.InvalidKindError

For example:

>>> import lumache
>>> lumache.get_random_ingredients()
['shells', 'gorgonzola', 'parsley']
