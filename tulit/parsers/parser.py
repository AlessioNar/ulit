from abc import ABC, abstractmethod
from lxml import etree
import os

class XMLParser(ABC):
    """
    Abstract base class for XML parsers.
    
    Attributes
    ----------
    schema : lxml.etree.XMLSchema or None
        The XML schema used for validation.
    valid : bool or None
        Indicates whether the XML file is valid against the schema.
    validation_errors : lxml.etree._LogEntry or None
        Validation errors if the XML file is invalid.
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
        None
        """
        self.schema = None
        self.valid = None
        self.validation_errors = None
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
    
    def load_schema(self, schema):
        """
        Loads the XSD schema for XML validation using an absolute path.
        
        Parameters
        ----------
        schema : str
            The path to the XSD schema file.
        
        Returns
        -------
        None
        """
        try:
            # Resolve the absolute path to the XSD file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(base_dir, 'assets', schema)

            # Parse the schema
            with open(schema_path, 'r') as f:
                schema_doc = etree.parse(f)
                self.schema = etree.XMLSchema(schema_doc)
            print("Schema loaded successfully.")
        except Exception as e:
            print(f"Error loading schema: {e}")

    def validate(self, format, file: str) -> bool:
        """
        Validates an XML file against the loaded XSD schema.
        
        Parameters
        ----------
        format : str
            The format of the XML file (e.g., 'Akoma Ntoso', 'Formex 4').        
        file : str
            Path to the XML file to validate.    
        
        Returns:
        --------
        bool
            Sets the valid attribute to True if the file is valid, False otherwise.
        """
        if not self.schema:
            print("No schema loaded. Please load an XSD schema first.")
            return None

        try:
            with open(file, 'r', encoding='utf-8') as f:
                xml_doc = etree.parse(f)
                self.schema.assertValid(xml_doc)
            print(f"{file} is a valid {format} file.")
            self.valid = True
        except etree.DocumentInvalid as e:
            print(f"{file} is not a valid {format} file. Validation errors: {e}")
            self.valid = False
            self.validation_errors = e.error_log
        except Exception as e:
            print(f"An error occurred during validation: {e}")
            self.valid = False
    
    def get_root(self, file: str):
        """
        Parses an XML file and returns its root element.

        Parameters
        ----------
        file : str
            Path to the XML file.

            
        Returns
        -------
        None
        """
        with open(file, 'r', encoding='utf-8') as f:
            tree = etree.parse(f)
            self.root = tree.getroot()

        
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
    
    def get_preface(self, preface_xpath, paragraph_xpath) -> None:
        """
        Extracts paragraphs from the preface section of the document.

        Args
        ----
        preface_xpath : str
            XPath expression to locate the preface element. For Akoma Ntoso, this is usually './/akn:preface', while for Formex it is './/TITLE'.
        paragraph_xpath : str
            XPath expression to locate the paragraphs within the preface. For Akoma Ntoso, this is usually './/akn:p', while for Formex it is './/P'.
        
        Returns
        -------
        list or None
            List of strings containing the text content of each paragraph
            in the preface. Returns None if no preface is found.
        """
        preface = self.root.find(preface_xpath, namespaces=self.namespaces)
        if preface is not None:
            paragraphs = []
            for p in preface.findall(paragraph_xpath, namespaces=self.namespaces):
                # Join all text parts in <p>, removing any inner tags
                paragraph_text = ''.join(p.itertext()).strip()
                paragraphs.append(paragraph_text)

        self.preface = ' '.join(paragraphs)
    
    ### Enacting terms block
    def get_body(self, body_xpath) -> None:
        """
        Extracts the body element from the document.

        Args
        ----
        body_xpath : str
            XPath expression to locate the body element. For Akoma Ntoso, this is usually './/akn:body', while for Formex it is './/ENACTING.TERMS'.
        
        Returns
        -------
        None
            Updates the instance's body attribute with the found body element.
        """
        # Use the namespace-aware find
        self.body = self.root.find(body_xpath, namespaces=self.namespaces)
        if self.body is None:
            # Fallback: try without namespace
            self.body = self.root.find(body_xpath)