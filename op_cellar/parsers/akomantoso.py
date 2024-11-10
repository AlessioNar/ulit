from .parser import Parser
import re
#import xml.etree.ElementTree as ET
from lxml import etree


class AkomaNtosoParser(Parser):
    """
    A parser for Akoma Ntoso files, extracting and processing their content.
    """
    def __init__(self, celex=None):
        """
        Initializes the parser
        
        Args:
            celex (str): Optional CELEX identifier for the document.
        """
        self.p_elements = []
        # Define the namespace mapping
        self.namespaces = {
            'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
            'fmx': 'http://formex.publications.europa.eu/schema/formex-05.56-20160701.xd'

        }
    
    def remove_node(self, tree, node):
        # Step 1: Remove all node elements from the recitals_section
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
        Parses the XML file and returns the root element.
        
        Args:
            file (str): Path to the XML file
        """
        with open(file, 'r', encoding='utf-8') as f:
            tree = etree.parse(f)
            self.root = tree.getroot()
            return self.root
        
    def get_meta_identification(self):
        """Extracts data from the <identification> element within <meta>."""
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
        """Extracts <FRBRWork> related data."""
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
        """Extracts <FRBRExpression> related data."""
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
        """Extracts <FRBRManifestation> related data."""
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
        """Extracts data from the <references> element within <meta>."""
        references = self.root.find('.//akn:meta/akn:references/akn:TLCOrganization', namespaces=self.namespaces)
        if references is None:
            return None

        return {
            'eId': references.get('eId'),
            'href': references.get('href'),
            'showAs': references.get('showAs')
        }
    
    def get_meta_proprietary(self):
        """Extracts data from the <proprietary> element within <meta>."""
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
        """Extracts paragraphs and nested elements within the <preface> tag."""
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
        """Extracts the high-level preamble data including formula text and citations."""
        preamble_data = {
            'formula': self.get_preamble_formula(),
            'citations': self.get_preamble_citations(),
            'recitals': self.get_preamble_recitals()
        }
        return preamble_data
    
    def get_preamble_formula(self):

        """Extracts the bare text from the <formula> element within <preamble>."""
        formula = self.root.find('.//akn:preamble/akn:formula', namespaces=self.namespaces)
        if formula is None:
            return None

        # Extract text from <p> within <formula>
        formula_text = ' '.join(p.text.strip() for p in formula.findall('akn:p', namespaces=self.namespaces) if p.text)
        return formula_text
    
    def get_preamble_citations(self):
        """Extracts text from each <citation> element within <citations> in <preamble>."""
        citations_section = self.root.find('.//akn:preamble/akn:citations', namespaces=self.namespaces)
        if citations_section is None:
            return None

        citations_text = []
        for citation in citations_section.findall('akn:citation', namespaces=self.namespaces):
            # Collect bare text within each <p> in <citation>
            
            citation_text = "".join(citation.itertext()).strip()
            
            # Add any additional text from <authorialNote> within <citation>
            authorial_notes = []
            for note in citation.findall('.//akn:authorialNote/akn:p', namespaces=self.namespaces):
                note_text = ''.join(note.itertext()).strip()
                authorial_notes.append(note_text)

            citations_text.append({
                'citation_text': citation_text,
                'authorial_notes': authorial_notes
            })
        
        return citations_text
    
    def get_preamble_recitals(self):
        """Extracts text from each <recital> element within <recitals> in <preamble>."""
        
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
        Extracts the act element from the Akoma Ntoso file.
        """
        # Use the namespace-aware find
        self.act = self.root.find('.//akn:act', namespaces=self.namespaces)
        if self.act is None:
            # Fallback: try without namespace
            self.act = self.root.find('.//act')
        
    def get_body(self) -> None:
        """
        Extracts the body element from the Akoma Ntoso file.
        """
        # Use the namespace-aware find
        self.body = self.root.find('.//akn:body', namespaces=self.namespaces)
        if self.body is None:
            # Fallback: try without namespace
            self.body = self.root.find('.//body')
    
    def get_chapters(self) -> None:        
        """Extracts chapters from the XML, including eId, num, and heading if available."""
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

        return self.chapters


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



    def extract_provisions(self) -> list[dict]:
        """
        Extracts provisions from paragraph elements, returning sentences with their eId.
        
        Returns:
            list[dict]: List of provisions with CELEX ID, sentence text, and eId.
        """
        provisions = []
        for p_element in self.p_elements:
            eId, sentences = self.process_element(p_element)
            for sentence in sentences:
                provisions.append({
                    "celex": self.celex,
                    "eId": eId,
                    "sentence": sentence,
                })
        return provisions

    def process_element(self, element) -> tuple:
        """
        Extracts eId and sentences from an XML element after masking references and dates.
        
        Args:
            element (ET.Element): The paragraph element.
        
        Returns:
            tuple[str, list[str]]: eId and list of sentences.
        """
        eId = element.get("eId", "")
        element, refs, dates = self.mask_references_and_dates(element)
        text = self.merge_dom_children(element)
        sentences = self.process_text(text)
        sentences = self.unmask_element(sentences, refs, dates)
        return eId, sentences

