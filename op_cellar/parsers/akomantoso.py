from .parser import Parser
import re
from lxml import etree

class AkomaNtosoParser(Parser):
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
        Initializes the parser
        
        """
        # Define the namespace mapping
        self.namespaces = {
            'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
            'an': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
            'fmx': 'http://formex.publications.europa.eu/schema/formex-05.56-20160701.xd'


        }
    
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

        frbr_data = {
            'work': self._get_frbr_work(identification),
            'expression': self._get_frbr_expression(identification),
            'manifestation': self._get_frbr_manifestation(identification)
        }
        return frbr_data
    
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

        return {
            'eId': references.get('eId'),
            'href': references.get('href'),
            'showAs': references.get('showAs')
        }
    
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

        return {
            'file': document_ref.get('FILE'),
            'coll': document_ref.find('fmx:COLL', namespaces=self.namespaces).text,
            'year': document_ref.find('fmx:YEAR', namespaces=self.namespaces).text,
            'lg_doc': proprietary.find('fmx:LG.DOC', namespaces=self.namespaces).text,
            'no_seq': proprietary.find('fmx:NO.SEQ', namespaces=self.namespaces).text
            # Add other elements as needed
        }
    
    def get_preface(self):
        """
            Extracts paragraphs from the preface section of the document.

            Returns
            -------
            list or None
                List of strings containing the text content of each paragraph
                in the preface. Returns None if no preface is found.
            """
        preface = self.root.find('.//akn:preface', namespaces=self.namespaces)
        if preface is None:
            return None

        paragraphs = []
        for p in preface.findall('akn:p', namespaces=self.namespaces):
            # Join all text parts in <p>, removing any inner tags
            paragraph_text = ''.join(p.itertext()).strip()
            paragraphs.append(paragraph_text)

        return paragraphs
    
    def get_preamble(self):
        """
        Extracts complete preamble data from the document.

        Returns
        -------
        dict
            Dictionary containing preamble components with keys:
            - 'formula': Formula text
            - 'citations': List of citations
            - 'recitals': List of recitals
        """
        preamble_data = {
            'formula': self.get_preamble_formula(),
            'citations': self.get_preamble_citations(),
            'recitals': self.get_preamble_recitals()
        }
        return preamble_data
    
    def get_preamble_formula(self):
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
    
    def get_preamble_citations(self):
        """
        Extracts citations from the preamble.

        Returns
        -------
        list or None
            List of dictionaries containing citation text without the associated
            authorial notes. Returns None if no citations are found.
        """
        citations_section = self.root.find('.//akn:preamble/akn:citations', namespaces=self.namespaces)
        if citations_section is None:
            return None
        # Removing all authorialNote nodes
        citations_section = self.remove_node(citations_section, './/akn:authorialNote')

        citations_text = []
        for citation in citations_section.findall('akn:citation', namespaces=self.namespaces):
            # Collect bare text within each <p> in <citation>            
            citation_text = "".join(citation.itertext()).strip()

            citations_text.append({
                'citation_text': citation_text,
            })
        
        return citations_text
    
    def get_preamble_recitals(self):
        """
        Extracts recitals from the preamble.

        Returns
        -------
        list or None
            List of dictionaries containing recital text and eId for each
            recital. Returns None if no recitals are found.
        """
        recitals_section = self.root.find('.//akn:preamble/akn:recitals', namespaces=self.namespaces)
        if recitals_section is None:
            return None

        recitals_text = []
                
        # Intro
        recitals_intro = recitals_section.find('akn:intro', namespaces=self.namespaces)
        recitals_intro_eId = recitals_intro.get('eId')
        recitals_intro_text = ' '.join(p.text.strip() for p in recitals_intro.findall('akn:p', namespaces=self.namespaces) if p.text)
        recitals_text.append({
            'recital_text': recitals_intro_text,
            'eId': recitals_intro_eId
        })

        # Removing all authorialNote nodes
        recitals_section = self.remove_node(recitals_section, './/akn:authorialNote')

        # Step 2: Process each <recital> element in the recitals_section without the <authorialNote> elements
        for recital in recitals_section.findall('akn:recital', namespaces=self.namespaces):
            eId = str(recital.get('eId'))

            # Extract text from remaining <akn:p> elements
            recital_text = ' '.join(' '.join(p.itertext()).strip() for p in recital.findall('akn:p', namespaces=self.namespaces))

            # Remove any double spaces in the concatenated recital text
            recital_text = re.sub(r'\s+', ' ', recital_text)

            # Append the cleaned recital text and eId to the list
            recitals_text.append({
                'recital_text': recital_text,
                'eId': eId
            })

        return recitals_text
    
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
        
    def get_body(self) -> None:
        """
        Extracts the body element from the document.

        Returns
        -------
        None
            Updates the instance's body attribute with the found body element.
        """
        # Use the namespace-aware find
        self.body = self.root.find('.//akn:body', namespaces=self.namespaces)
        if self.body is None:
            # Fallback: try without namespace
            self.body = self.root.find('.//body')
    
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
        self.chapters = []  # Reset chapters list
        
        # Find all <chapter> elements in the body
        for chapter in self.root.findall('.//akn:chapter', namespaces=self.namespaces):
            eId = chapter.get('eId')
            chapter_num = chapter.find('akn:num', namespaces=self.namespaces)
            chapter_heading = chapter.find('akn:heading', namespaces=self.namespaces)
            
            # Add chapter data to chapters list
            self.chapters.append({
                'eId': eId,
                'chapter_num': chapter_num.text if chapter_num is not None else None,
                'chapter_heading': ''.join(chapter_heading.itertext()).strip() if chapter_heading is not None else None
            })

        return None
    
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

    def parse(self, file: str) -> list[dict]:
        """
        Parses an Akoma Ntoso file to extract provisions as individual sentences.
        
        Args:
            file (str): The path to the Akoma Ntoso XML file.
        
        Returns:
            list[dict]: List of extracted provisions with CELEX ID, sentence text, and eId.
        """
        self.get_root(file)
        self.get_body()
        self.get_chapters()
        self.get_articles()


