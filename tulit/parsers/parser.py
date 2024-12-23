from abc import ABC, abstractmethod
from lxml import etree


class XMLParser(ABC):
    """
    Abstract base class for XML parsers.
    
    Attributes
    ----------
    root : lxml.etree._Element
        Root element of the XML document.
    namespaces : dict
        Dictionary containing XML namespaces.
    preface : str or None
        Extracted preface text from the XML document.
    preamble : lxml.etree.Element or None
        The preamble section of the XML document.
    formula : None
        Placeholder for future use.
    citations : list or None
        List of extracted citations from the preamble.
    recitals : list or None
        List of extracted recitals from the preamble.
    body : lxml.etree.Element or None
        The body section of the XML document.
    chapters : list
        List of extracted chapters from the body.
    articles : list
        List of extracted articles from the body.
    articles_text : list
        List of extracted article texts.
    conclusions : None
        Placeholder for future use.
    """
    
    def __init__(self):
        """
        Initializes the Parser object.

        Parameters
        ----------
        file : str
            Path to the XML file.
        namespaces : dict
            Dictionary containing XML namespaces.
        """
        self.root = None
        self.namespaces = {}
        
        self.preface = None

        self.preamble = None
        self.formula = None    
        self.citations = None
        self.recitals = None
    
        self.body = None
        self.chapters = []
        self.articles = []
        self.conclusions = None
        
        self.articles_text = []
        
    @abstractmethod
    def parse(self):
        """
        Abstract method to parse the data. This method must be implemented by the subclass.
        """
        pass
    
    def get_root(self, file: str):
        """
        Parses an XML file and returns its root element.

        Parameters
        ----------
        file : str
            Path to the XML file.

        Returns
        -------
        lxml.etree._Element
            Root element of the parsed XML document.
        """
        with open(file, 'r', encoding='utf-8') as f:
            tree = etree.parse(f)
            self.root = tree.getroot()
            return self.root
        
    def remove_node(self, tree, node):
        """
        Removes specified nodes from the XML tree while preserving their tail text.
        
        Parameters
        ----------
        tree : lxml.etree._Element
            The XML tree or subtree to process.
        node : str
            XPath expression identifying the nodes to remove.
        
        Returns
        -------
        lxml.etree._Element
            The modified XML tree with specified nodes removed.
        """
        if tree.findall(node, namespaces=self.namespaces) is not None:
            for item in tree.findall(node, namespaces=self.namespaces):
                text = ' '.join(item.itertext()).strip()
                
                # Find the parent and remove the <node> element
                parent = item.getparent()
                tail_text = item.tail
                if parent is not None:
                    parent.remove(item)

                # Preserve tail text if present
                if tail_text:
                    if parent.getchildren():
                        # If there's a previous sibling, add the tail to the last child
                        previous_sibling = parent.getchildren()[-1]
                        previous_sibling.tail = (previous_sibling.tail or '') + tail_text
                    else:
                        # If no siblings, add the tail text to the parent's text
                        parent.text = (parent.text or '') + tail_text
        
        return tree