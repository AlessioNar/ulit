from .parser import XMLParser
import re
from lxml import etree
import os

class AkomaNtosoParser(XMLParser):
    """
    A parser for processing and extracting content from Akoma Ntoso XML files.

    The parser handles XML documents following the Akoma Ntoso schema for legal documents,
    providing methods to extract various components like metadata, preamble, articles,
    and chapters.

    Attributes
    ----------
    namespaces : dict
        Dictionary mapping namespace prefixes to their URIs.
    """
    def __init__(self):
        """
        Initializes the parser.
        """
        super().__init__()
        self.meta = None
    
        self.meta_identification = None    
        self.meta_proprietary = None
        self.meta_references = None
        
        self.act = None
    
        
        self.debug_info = {}

        
        # Define the namespace mapping
        self.namespaces = {
            'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
            'an': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
            'fmx': 'http://formex.publications.europa.eu/schema/formex-05.56-20160701.xd'


        }

    ### Metadata block
    def get_meta(self):
        """
        Extracts metadata from the document.
        """
        meta_data = {
            "meta_identification" : self.get_meta_identification(),
            "meta_proprietary" : self.get_meta_proprietary(),
            "meta_references" : self.get_meta_references()
        }

        self.meta = meta_data
                
    def get_meta_identification(self):
        """
        Extracts identification metadata from the XML document.

        Retrieves data from the <identification> element within <meta>,
        including FRBR Work, Expression, and Manifestation information.

        Returns
        -------
        dict or None
            Dictionary containing FRBR metadata with keys 'work', 'expression',
            and 'manifestation'. Returns None if no identification data is found.
        """
        identification = self.root.find('.//akn:meta/akn:identification', namespaces=self.namespaces)
        if identification is None:
            return None

        meta_identification = {
            'work': self._get_frbr_work(identification),
            'expression': self._get_frbr_expression(identification),
            'manifestation': self._get_frbr_manifestation(identification)
        }
        return meta_identification
    
    def _get_frbr_work(self, identification):
        """
        Extracts FRBR Work metadata from the identification element.

        Parameters
        ----------
        identification : lxml.etree._Element
            The identification element containing FRBR Work data.

        Returns
        -------
        dict or None
            Dictionary containing FRBR Work metadata including URIs, dates,
            and other work-level identifiers. Returns None if no work data is found.
        """
        frbr_work = identification.find('akn:FRBRWork', namespaces=self.namespaces)
        if frbr_work is None:
            return None

        return {
            'FRBRthis': frbr_work.find('akn:FRBRthis', namespaces=self.namespaces).get('value'),
            'FRBRuri': frbr_work.find('akn:FRBRuri', namespaces=self.namespaces).get('value'),
            'FRBRalias': frbr_work.find('akn:FRBRalias', namespaces=self.namespaces).get('value'),
            'FRBRdate': frbr_work.find('akn:FRBRdate', namespaces=self.namespaces).get('date'),
            'FRBRauthor': frbr_work.find('akn:FRBRauthor', namespaces=self.namespaces).get('href'),
            'FRBRcountry': frbr_work.find('akn:FRBRcountry', namespaces=self.namespaces).get('value'),
            'FRBRnumber': frbr_work.find('akn:FRBRnumber', namespaces=self.namespaces).get('value')
        }
    
    def _get_frbr_expression(self, identification):
        """
        Extracts FRBR Expression metadata from the identification element.

        Parameters
        ----------
        identification : lxml.etree._Element
            The identification element containing FRBR Expression data.
        
        Returns
        -------
        dict or None
            Dictionary containing FRBR Expression metadata including URIs, dates,
            language, and other expression-level identifiers. Returns None if no
            expression data is found.
        """

        frbr_expression = identification.find('akn:FRBRExpression', namespaces=self.namespaces)
        if frbr_expression is None:
            return None

        return {
            'FRBRthis': frbr_expression.find('akn:FRBRthis', namespaces=self.namespaces).get('value'),
            'FRBRuri': frbr_expression.find('akn:FRBRuri', namespaces=self.namespaces).get('value'),
            'FRBRdate': frbr_expression.find('akn:FRBRdate', namespaces=self.namespaces).get('date'),
            'FRBRauthor': frbr_expression.find('akn:FRBRauthor', namespaces=self.namespaces).get('href'),
            'FRBRlanguage': frbr_expression.find('akn:FRBRlanguage', namespaces=self.namespaces).get('language')
        }
    
    def _get_frbr_manifestation(self, identification):
        """
        Extracts FRBR Manifestation metadata from the identification element.

        Parameters
        ----------
        identification : lxml.etree._Element
            The identification element containing FRBR Manifestation data.

        Returns
        -------
        dict or None
            Dictionary containing FRBR Manifestation metadata including URIs,
            dates, and other manifestation-level identifiers. Returns None if
            no manifestation data is found.
        """
        frbr_manifestation = identification.find('akn:FRBRManifestation', namespaces=self.namespaces)
        if frbr_manifestation is None:
            return None

        return {
            'FRBRthis': frbr_manifestation.find('akn:FRBRthis', namespaces=self.namespaces).get('value'),
            'FRBRuri': frbr_manifestation.find('akn:FRBRuri', namespaces=self.namespaces).get('value'),
            'FRBRdate': frbr_manifestation.find('akn:FRBRdate', namespaces=self.namespaces).get('date'),
            'FRBRauthor': frbr_manifestation.find('akn:FRBRauthor', namespaces=self.namespaces).get('href')
        }
    
    def get_meta_references(self):
        """
        Extracts reference metadata from the XML document.

        Retrieves data from the <references> element within <meta>,
        specifically focusing on TLCOrganization elements.

        Returns
        -------
        dict or None
            Dictionary containing reference metadata including eId, href,
            and showAs attributes. Returns None if no reference data is found.
        """
        references = self.root.find('.//akn:meta/akn:references/akn:TLCOrganization', namespaces=self.namespaces)
        if references is None:
            return None

        meta_references = {
            'eId': references.get('eId'),
            'href': references.get('href'),
            'showAs': references.get('showAs')
        }
        return meta_references
    
    def get_meta_proprietary(self):
        """
        Extracts proprietary metadata from the XML document.

        Retrieves data from the <proprietary> element within <meta>,
        including document reference information.

        Returns
        -------
        dict or None
            Dictionary containing proprietary metadata including file, collection,
            year, language, and sequence number. Returns None if no proprietary
            data is found.
        """
        proprietary = self.root.find('.//akn:meta/akn:proprietary', namespaces=self.namespaces)
        if proprietary is None:
            return None

        document_ref = proprietary.find('fmx:DOCUMENT.REF', namespaces=self.namespaces)
        if document_ref is None:
            return None

        meta_proprietary = {
            'file': document_ref.get('FILE'),
            'coll': document_ref.find('fmx:COLL', namespaces=self.namespaces).text,
            'year': document_ref.find('fmx:YEAR', namespaces=self.namespaces).text,
            'lg_doc': proprietary.find('fmx:LG.DOC', namespaces=self.namespaces).text,
            'no_seq': proprietary.find('fmx:NO.SEQ', namespaces=self.namespaces).text
            # Add other elements as needed
        }

        return meta_proprietary
    
    def get_formula(self):
        """
        Extracts formula text from the preamble.

        Returns
        -------
        str or None
            Concatenated text from all paragraphs within the formula element.
            Returns None if no formula is found.
        """
        formula = self.root.find('.//akn:preamble/akn:formula', namespaces=self.namespaces)
        if formula is None:
            return None

        # Extract text from <p> within <formula>
        formula_text = ' '.join(p.text.strip() for p in formula.findall('akn:p', namespaces=self.namespaces) if p.text)
        return formula_text
    
    def get_citations(self) -> list:
        """
        Extracts citations from the preamble.

        Returns
        -------
        list
            List of dictionaries containing citation data with keys:
            - 'eId': Citation identifier, which is retrieved from the 'eId' attribute
            - 'text': Citation text
        """
        def extract_eId(citation, index):
            return citation.get('eId')

        return super().get_citations(
            citations_xpath='.//akn:citations',
            citation_xpath='.//akn:citation',
            extract_eId=extract_eId
        )
    
    def get_recitals(self):
        """
        Extracts recitals from the preamble.

        Returns
        -------
        list or None
            List of dictionaries containing recital text and eId for each
            recital. Returns None if no recitals are found.
        """
        recitals_section = self.preamble.find('.//akn:recitals', namespaces=self.namespaces)
        if recitals_section is None:
            return None

        recitals = []
                
        # Intro
        recitals_intro = recitals_section.find('.//akn:intro', namespaces=self.namespaces)
        recitals_intro_eId = recitals_intro.get('eId')
        recitals_intro_text = ' '.join(p.text.strip() for p in recitals_intro.findall('.//akn:p', namespaces=self.namespaces) if p.text)
        recitals.append({
            'recital_text': recitals_intro_text,
            'eId': recitals_intro_eId
        })

        # Removing all authorialNote nodes
        recitals_section = self.remove_node(recitals_section, './/akn:authorialNote')

        # Step 2: Process each <recital> element in the recitals_section without the <authorialNote> elements
        for recital in recitals_section.findall('.//akn:recital', namespaces=self.namespaces):
            eId = str(recital.get('eId'))

            # Extract text from remaining <akn:p> elements
            recital_text = ' '.join(' '.join(p.itertext()).strip() for p in recital.findall('.//akn:p', namespaces=self.namespaces))

            # Remove any double spaces in the concatenated recital text
            recital_text = re.sub(r'\s+', ' ', recital_text)

            # Append the cleaned recital text and eId to the list
            recitals.append({
                'recital_text': recital_text,
                'eId': eId
            })

        self.recitals = recitals
    
    ### Act block
    def get_act(self) -> None:
        """
        Extracts the act element from the document.

        Returns
        -------
        None
            Updates the instance's act attribute with the found act element.
        """
        # Use the namespace-aware find
        self.act = self.root.find('.//akn:act', namespaces=self.namespaces)
        if self.act is None:
            # Fallback: try without namespace
            self.act = self.root.find('.//act')
        
    def get_chapters(self, chapter_xpath, num_xpath, heading_xpath) -> None:        
        """
        Extracts chapter information from the document.
        
        Parameters
        ----------
        chapter_xpath : str
            XPath expression to locate the chapter elements.
        num_xpath : str
            XPath expression to locate the chapter number within each chapter element.
        heading_xpath : str
            XPath expression to locate the chapter heading within each chapter element.

        Returns
        -------
        list
            List of dictionaries containing chapter data with keys:
            - 'eId': Chapter identifier
            - 'chapter_num': Chapter number
            - 'chapter_heading': Chapter heading text
        """        
        # Find all <chapter> elements in the body
        for chapter in self.body.findall(chapter_xpath, namespaces=self.namespaces):
            eId = chapter.get('eId')
            chapter_num = chapter.find(num_xpath, namespaces=self.namespaces)
            chapter_heading = chapter.find(heading_xpath, namespaces=self.namespaces)
            
            # Add chapter data to chapters list
            self.chapters.append({
                'eId': eId,
                'chapter_num': chapter_num.text if chapter_num is not None else None,
                'chapter_heading': ''.join(chapter_heading.itertext()).strip() if chapter_heading is not None else None
            })

    
    def get_articles(self) -> None:
        """
        Extracts article information from the document.

        Returns
        -------
        list
            List of dictionaries containing article data with keys:
            - 'eId': Article identifier
            - 'article_num': Article number
            - 'article_title': Article title
            - 'article_text': List of dictionaries with eId and text content
        """
        self.articles = []  # Reset articles list

        # Removing all authorialNote nodes
        self.body = self.remove_node(self.body, './/akn:authorialNote')

        # Find all <article> elements in the XML
        for article in self.body.findall('.//akn:article', namespaces=self.namespaces):
            eId = article.get('eId')
            
            # Find the main <num> element representing the article number
            article_num = article.find('akn:num', namespaces=self.namespaces)
            article_num_text = article_num.text if article_num is not None else None

            # Find a secondary <num> or <heading> to represent the article title or subtitle, if present
            article_title_element = article.find('akn:heading', namespaces=self.namespaces)
            if article_title_element is None:
                # If <heading> is not found, use the second <num> as the title if it exists
                article_title_element = article.findall('akn:num', namespaces=self.namespaces)[1] if len(article.findall('akn:num', namespaces=self.namespaces)) > 1 else None
            # Get the title text 
            article_title_text = article_title_element.text if article_title_element is not None else None

            # So I need to find another parsing strategy as the non-normative nature of Akoma Ntoso makes it more complicated to parse it.
            # This function first finds all of the p tags
            # Then Identifies the closest parent of the p tag containing an attribute eId
            # Then it concatenates p tags based on common eIds
            # And finally creates a list of dictionaries composed by the eId and the text of each element
            article_text = self.get_text_by_eId(article)
        
            # Append the article data to the articles list
            self.articles.append({
                'eId': eId,
                'article_num': article_num_text,
                'article_title': article_title_text,
                # This is not really text - rather a list of dictionaries composed by the eId and the text of each element
                'article_text': article_text
            })

        return self.articles
    
    def get_text_by_eId(self, node):
        """
        Groups paragraph text by their nearest parent element with an eId attribute.

        Parameters
        ----------
        node : lxml.etree._Element
            XML node to process for text extraction.

        Returns
        -------
        list
            List of dictionaries containing:
            - 'eId': Identifier of the nearest parent with an eId
            - 'text': Concatenated text content
        """
        elements = []
        # Find all <p> elements
        for p in node.findall('.//akn:p', namespaces=self.namespaces):
            # Traverse up to find the nearest parent with an eId
            current_element = p
            eId = None
            while current_element is not None:
                eId = current_element.get('eId')
                if eId:
                    break
                current_element = current_element.getparent()  # Traverse up

            # If an eId is found, add <p> text to the eId_text_map
            if eId:
                # Capture the full text within the <p> tag, including nested elements
                p_text = ''.join(p.itertext()).strip()
                element = {
                    'eId': eId,
                    'text': p_text
                }
                elements.append(element)
        return elements
    
    def get_conclusions(self):
        """
        Extracts conclusions information from the document.

        Returns
        -------
        None
        """
        conclusions_section = self.root.find('.//akn:conclusions', namespaces=self.namespaces)
        if conclusions_section is None:
            return None

        # Find the container with signatures
        container = conclusions_section.find('.//akn:container[@name="signature"]', namespaces=self.namespaces)
        if container is None:
            return None

        # Extract date from the first <signature>
        date_element = container.find('.//akn:date', namespaces=self.namespaces)
        signature_date = date_element.text if date_element is not None else None

        # Extract all signatures
        signatures = []
        for p in container.findall('akn:p', namespaces=self.namespaces):
            # For each <p>, find all <signature> tags
            paragraph_signatures = []
            for signature in p.findall('akn:signature', namespaces=self.namespaces):
                # Collect text within the <signature>, including nested elements
                signature_text = ''.join(signature.itertext()).strip()
                paragraph_signatures.append(signature_text)

            # Add the paragraph's signatures as a group
            if paragraph_signatures:
                signatures.append(paragraph_signatures)

        # Store parsed conclusions data
        self.conclusions = {
            'date': signature_date,
            'signatures': signatures
        }
    
    def parse(self, file: str) -> list[dict]:
        """
        Parses an Akoma Ntoso file to extract provisions as individual sentences.

        This method sequentially calls various parsing functions to extract metadata,
        preface, preamble, body, chapters, articles, and conclusions from the XML file.
        It logs errors encountered during parsing and provides debug information about
        the structure of the document.

        Args:
            file (str): The path to the Akoma Ntoso XML file.


        """
        debug_info = {}
        try:
            self.load_schema('akomantoso30.xsd')
            self.validate(file, format='Akoma Ntoso')
            if self.valid == True:
                try:
                    self.get_root(file)
                    print("Root element loaded successfully.")
                except Exception as e:
                    print(f"Error in get_root: {e}")

                try:
                    self.get_meta()
                    debug_info['meta'] = self.meta if hasattr(self, 'meta') else "Meta not parsed."
                    print("Meta parsed successfully.")
                except Exception as e:
                    print(f"Error in get_meta: {e}")

                try:
                    self.get_preface(preface_xpath='.//akn:preface', paragraph_xpath='akn:p')
                    debug_info['preface'] = self.preface if hasattr(self, 'preface') else 0
                    print(f"Preface parsed successfully.")
                except Exception as e:
                    print(f"Error in get_preface: {e}")
                try:
                    self.get_preamble(preamble_xpath='.//akn:preamble', notes_xpath=".//akn:authorialNote")
                    print(f"Preamble parsed successfully.")
                except Exception as e:
                    print(f"Error in get_preamble: {e}")
                try:
                    self.get_citations(citations_xpath='.//akn:citations', citation_xpath='.//akn:citation')
                    print(f"Citations parsed successfully.")
                except Exception as e:
                    print(f"Error in get_citations: {e}")
                try:
                    self.get_body(body_xpath='.//akn:body')
                    print("Body parsed successfully.")
                except Exception as e:
                    print(f"Error in get_body: {e}")

                try:
                    self.get_chapters(chapter_xpath='.//akn:chapter', num_xpath='.//akn:num', heading_xpath='.//akn:heading')
                    debug_info['chapters'] = len(self.chapters) if hasattr(self, 'chapters') else 0
                    print(f"Chapters parsed successfully. Number of chapters: {debug_info['chapters']}")
                except Exception as e:
                    print(f"Error in get_chapters: {e}")

                try:
                    self.get_articles()
                    debug_info['articles'] = len(self.articles) if hasattr(self, 'articles') else 0
                    print(f"Articles parsed successfully. Number of articles: {debug_info['articles']}")
                except Exception as e:
                    print(f"Error in get_articles: {e}")

                try:
                    self.get_conclusions()
                    debug_info['conclusions'] = self.conclusions if hasattr(self, 'conclusions') else "Conclusions not parsed."
                    print(f"Conclusions parsed successfully. ")
                except Exception as e:
                    print(f"Error in get_conclusions: {e}")
                
        except Exception as e:
            print(f'Invalid Akoma Ntoso file: parsing may not work or work only partially: {e}')
