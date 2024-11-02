from abc import ABC, abstractmethod

from .formex import Formex4Parser
from .akomantoso import AkomaNtosoParser
from .html import HTMLParser

class Parser(ABC):
    @abstractmethod
    def parse(self, data):
        pass

class XMLParser(Parser):
    def parse(self, data):
        # Your XML parsing logic here
        pass

# Usage
parsers = {
    'html': HTMLParser(),
    'xml': XMLParser(),
    'formex4': Formex4Parser(),
    'akoma_ntoso': AkomaNtosoParser(),
}

def parse_data(data, format, granularity='article'):
    parser = parsers.get(format.lower())
    if parser:
        return parser.parse(data, granularity)
    else:
        raise ValueError('Unsupported format')
