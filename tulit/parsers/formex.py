import re
import os

from lxml import etree
from .parser import XMLParser

class Formex4Parser(XMLParser):
    """
    A parser for processing and extracting content from Formex XML files.

    The parser handles XML documents following the Formex schema for legal documents,
    providing methods to extract various components like metadata, preface, preamble,
    and articles.

    Attributes
    ----------

    metadata : dict
        Extracted metadata from the XML document.

    """

    def __init__(self):
        """
        Initializes the parser.
        """
        # Define the namespace mapping
        super().__init__()

        self.namespaces = {
            'fmx': 'http://formex.publications.europa.eu/schema/formex-05.56-20160701.xd'
        }

        self.metadata = {}

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
    
        
    def get_formula(self):
        """
        Extracts the formula from the preamble.

        Returns
        -------
        str
            Formula text from the preamble.
        """
        self.formula = self.preamble.findtext('PREAMBLE.INIT')
        
        return self.formula
    
    def get_citations(self, citations_xpath, citation_xpath):
        """
        Extracts citations from the preamble.

        Returns
        -------
        list
            List of dictionaries containing citation text.
        """
        citations_section = self.preamble.find(citations_xpath, namespaces=self.namespaces)
        if citations_section is None:
            return None
        
        citations = []
        for index, citation in enumerate(self.preamble.findall(citation_xpath)):
            citation_text = "".join(citation.itertext()).strip()  # Using itertext() to get all nested text
            citation_text = citation_text.replace('\n', '').replace('\t', '').replace('\r', '')  # remove newline and tab characters
            citation_text = re.sub(' +', ' ', citation_text)  # replace multiple spaces with a single space
            
            citations.append({
                'eId': index,
                'citation_text': citation_text
            })
                
        self.citations = citations

    
    def get_recitals(self):
        """
        Extracts recitals from the preamble.

        Returns
        -------
        list
            List of dictionaries containing recital text and eId for each recital.
        """
        #preamble_data["preamble_final"] = self.preamble.findtext('PREAMBLE.FINAL')

        recitals = []
        recitals.append({
            "eId": 'rec_0',
            "recital_text": self.preamble.findtext('.//GR.CONSID/GR.CONSID.INIT')
            })

        for recital in self.preamble.findall('.//CONSID'):
            recital_num = recital.findtext('.//NO.P')
            recital_text = "".join(recital.find('.//TXT').itertext()).strip()
            recitals.append({
                    "eId": recital_num, 
                    "recital_text": recital_text
                })
        self.recitals = recitals
        
   
    
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
        self.load_schema('formex4.xsd')
        self.validate(file, format = 'Formex 4')
        self.get_root(file)
        self.get_metadata()
        self.get_preface(preface_xpath='.//TITLE', paragraph_xpath='.//P')
        self.get_preamble(preamble_xpath='.//PREAMBLE', notes_xpath='.//NOTE')
        self.get_body(body_xpath='.//ENACTING.TERMS')
        self.get_chapters()
        self.get_articles()