# Import required functions
from setuptools import setup, find_packages

# Call setup function
setup(
    author="Alessio Nardin>",
    description="A generic package to query and retrieve documents from Cellar, the common data repository of the Publications Office of the European Union.",
    name="op_cellar",
    packages=find_packages(include=["op_cellar", "op_cellar.*"]),
    
    install_requires=[
        'requests>=2.32.3',
        'pandas>=2.2.3',
        'spacy>=3.7.6',
        'sparqlwrapper>=2.0.0',
        'beautifulsoup4>=4.12.3',
        'lxml>=5.3.0'

    ],

    version="0.0.1-alpha",
)
