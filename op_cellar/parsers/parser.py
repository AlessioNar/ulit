from abc import ABC, abstractmethod

class Parser(ABC):
    @abstractmethod
    def parse(self, data):
        pass

class XMLParser(Parser):
    def parse(self, data):
        # Your XML parsing logic here
        pass