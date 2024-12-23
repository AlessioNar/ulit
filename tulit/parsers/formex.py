import re
import os

from lxml import etree
from .parser import Parser

FMX_NAMESPACES = {
    'fmx': 'http://formex.publications.europa.eu/schema/formex-05.56-20160701.xd'
}

class Formex4Parser(Parser):
    """
    A parser for processing and extracting content from Formex XML files.

    The parser handles XML documents following the Formex schema for legal documents,
    providing methods to extract various components like metadata, preface, preamble,
    and articles.

    Attributes
    ----------
    namespaces : dict
        Dictionary mapping namespace prefixes to their URIs.
    """

    def __init__(self):
        """
        Initializes the parser.
        """
        # Define the namespace mapping
        self.namespaces = {}
        self.namespaces = FMX_NAMESPACES
        self.schema = None
        self.valid = None

        self.root = None
        self.metadata = {}
        
        self.preface = None
        
        self.preamble = None
        self.formula = None    
        self.citations = None
        self.recitals = None
    
        self.body = None
        self.chapters = []
        self.articles = []
    
        self.articles_text = []
        self.conclusions = None

    def load_schema(self):
        """
        Loads the XSD schema for XML validation using an absolute path.
        """
        try:
            # Resolve the absolute path to the XSD file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(base_dir, 'assets', 'formex4.xsd')

            # Parse the schema
            with open(schema_path, 'r') as f:
                schema_doc = etree.parse(f)
                self.schema = etree.XMLSchema(schema_doc)
            print("Schema loaded successfully.")
        except Exception as e:
            print(f"Error loading schema: {e}")

    def validate(self, file: str) -> bool:
        """
        Validates an XML file against the loaded XSD schema.

        Args:
            file (str): Path to the XML file to validate.

        Returns:
            bool: True if the XML file is valid, False otherwise.
        """
        if not self.schema:
            print("No schema loaded. Please load an XSD schema first.")
            return False

        try:
            with open(file, 'r', encoding='utf-8') as f:
                xml_doc = etree.parse(f)
                self.schema.assertValid(xml_doc)
            print(f"{file} is a valid Formex4 file.")
            self.valid = True
        except etree.DocumentInvalid as e:
            print(f"{file} is not a valid Formex4 file. Validation errors: {e}")
            self.valid = False
        except Exception as e:
            print(f"An error occurred during validation: {e}")
            self.valid = False

    def get_metadata(self):
        """
        Extracts metadata information from the BIB.INSTANCE section.

        Returns
        -------
        dict
            Extracted metadata.
        """
        metadata = {}
        bib_instance = self.root.find('BIB.INSTANCE')
        
        if bib_instance is not None:
            doc_ref = bib_instance.find('DOCUMENT.REF')
            if doc_ref is not None:
                metadata["file"] = doc_ref.get("FILE")
                metadata["collection"] = doc_ref.findtext('COLL')
                metadata["oj_number"] = doc_ref.findtext('NO.OJ')
                metadata["year"] = doc_ref.findtext('YEAR')
                metadata["language"] = doc_ref.findtext('LG.OJ')
                metadata["page_first"] = doc_ref.findtext('PAGE.FIRST')
                metadata["page_seq"] = doc_ref.findtext('PAGE.SEQ')
                metadata["volume_ref"] = doc_ref.findtext('VOLUME.REF')

            metadata["document_language"] = bib_instance.findtext('LG.DOC')
            metadata["sequence_number"] = bib_instance.findtext('NO.SEQ')
            metadata["total_pages"] = bib_instance.findtext('PAGE.TOTAL')

            no_doc = bib_instance.find('NO.DOC')
            if no_doc is not None:
                metadata["doc_format"] = no_doc.get("FORMAT")
                metadata["doc_type"] = no_doc.get("TYPE")
                metadata["doc_number"] = no_doc.findtext('NO.CURRENT')
        
        return metadata

    def get_preface(self):
        """
        Extracts title information from the TITLE section.

        Returns
        -------
        str
            Concatenated title text.
        """
        title_element = self.root.find('TITLE')
        title_text = ""
        
        if title_element is not None:
            for paragraph in title_element.iter('P'):
                paragraph_text = "".join(paragraph.itertext()).strip()
                title_text += paragraph_text + " "
        self.preface = title_text.strip()
        
        return self.preface
    
    def get_citations(self):
        """
        Extracts citations from the preamble.

        Returns
        -------
        list
            List of dictionaries containing citation text.
        """
        citations = []
        for index, citation in enumerate(self.preamble.findall('.//VISA')):
            citation_text = "".join(citation.itertext()).strip()  # Using itertext() to get all nested text
            citation_text = citation_text.replace('\n', '').replace('\t', '').replace('\r', '')  # remove newline and tab characters
            citation_text = re.sub(' +', ' ', citation_text)  # replace multiple spaces with a single space
            
            citations.append({
                'eId': index,
                'citation_text': citation_text
            })
                
        return citations 
    
    def get_recitals(self):
        """
        Extracts recitals from the preamble.

        Returns
        -------
        list
            List of dictionaries containing recital text and eId for each recital.
        """
        recitals = []
        # Extract each <TXT> element's text and corresponding <NO.P> number within <CONSID>
        for recital in self.preamble.findall('.//CONSID'):
            recital_num = recital.findtext('.//NO.P')
            recital_text = "".join(recital.find('.//TXT').itertext()).strip()
            recitals.append({
                    "eId": recital_num, 
                    "recital_text": recital_text
                })
        return recitals
        
    def get_preamble(self):
        """
        Extracts the preamble section, including initial statements and considerations.

        Returns
        -------
        dict
            Preamble details, including quotations and considerations.
        """
        preamble_data = {"initial_statement": None, "citations": [], "recitals_init": None, "recitals": [], "preamble_final": None}
        self.preamble = self.root.find('PREAMBLE')

        if self.preamble is not None:
            # Initial statement
            preamble_data["initial_statement"] = self.preamble.findtext('PREAMBLE.INIT')
            
            self.preamble = self.remove_node(self.preamble, './/NOTE')

            self.citations = self.get_citations()
            preamble_data["recitals_init"] = self.preamble.findtext('.//GR.CONSID/GR.CONSID.INIT')
            self.recitals = self.get_recitals()
            
            preamble_data["preamble_final"] = self.preamble.findtext('PREAMBLE.FINAL')
        
        return preamble_data
    
    def get_body(self) -> None:
        """
        Extracts the enacting terms element from the document.

        Returns
        -------
        None
            Updates the instance's body attribute with the found body element.
        """
        # Use the namespace-aware find
        self.body = self.root.find('.//fmx:ENACTING.TERMS', namespaces=self.namespaces)
        if self.body is None:
            # Fallback: try without namespace
            self.body = self.root.find('.//ENACTING.TERMS')
    
    def get_chapters(self) -> None:
        """
        Extracts chapter information from the document.

        Returns
        -------
        list
            List of dictionaries containing chapter data with keys:
            - 'eId': Chapter identifier
            - 'chapter_num': Chapter number
            - 'chapter_heading': Chapter heading text
        """
        self.chapters = []
        chapters = self.body.findall('.//TITLE', namespaces=self.namespaces)
        for index, chapter in enumerate(chapters):
            
            if len(chapter.findall('.//HT')) > 0:
                chapter_num = chapter.findall('.//HT')[0]
                if len(chapter.findall('.//HT')) > 1:      
                    chapter_heading = chapter.findall('.//HT')[1]
                    self.chapters.append({
            
                        "eId": index,
                        "chapter_num" : "".join(chapter_num.itertext()).strip(),
                        "chapter_heading": "".join(chapter_heading.itertext()).strip()
                    })
        

    def get_articles(self):
        """
        Extracts articles from the ENACTING.TERMS section.

        Returns
        -------
        list
            Articles with identifier and content.
        """
        self.articles = []
        if self.body is not None:
            for article in self.body.findall('.//ARTICLE'):
                article_data = {
                    "eId": article.get("IDENTIFIER"),
                    "article_num": article.findtext('.//TI.ART'),
                    "article_text": " ".join("".join(alinea.itertext()).strip() for alinea in article.findall('.//ALINEA'))
                }
                self.articles.append(article_data)
        else:
            print('No enacting terms XML tag has been found')
        

    def parse(self, file):
        """
        Parses a FORMEX XML document to extract metadata, title, preamble, and enacting terms.

        Args:
            file (str): Path to the FORMEX XML file.

        Returns
        -------
        dict
            Parsed data containing metadata, title, preamble, and articles.
        """
        self.load_schema()
        self.validate(file)
        self.get_root(file)
        self.get_metadata()
        self.get_preface()
        self.get_preamble()
        self.get_body()
        self.get_chapters()
        self.get_articles()