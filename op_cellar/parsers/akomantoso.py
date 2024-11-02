from .parser import Parser
import re
import xml.etree.ElementTree as ET

class AkomaNtosoParser(Parser):
    """
    A parser for Akoma Ntoso files, extracting and processing their content.
    """
    def __init__(self, celex=None):
        """
        Initializes the parser and sets the CELEX ID if provided.
        
        Args:
            celex (str): Optional CELEX identifier for the document.
        """
        self.celex = celex
        self.body = None
        self.p_elements = []

    def parse(self, file: str) -> list[dict]:
        """
        Parses an Akoma Ntoso file to extract provisions as individual sentences.
        
        Args:
            file (str): The path to the Akoma Ntoso XML file.
        
        Returns:
            list[dict]: List of extracted provisions with CELEX ID, sentence text, and eId.
        """
        # Step 1: Get the body of the document
        self.get_body(file)

        # Step 2: Extract top-level <p> tags
        self.get_p_tags()

        # Step 3: Extract provisions
        return self.extract_provisions()

    def get_body(self, file: str) -> None:
        """
        Extracts the body element from the Akoma Ntoso file.
        
        Args:
            file (str): Path to the Akoma Ntoso XML file.
        """
        tree = ET.parse(file)
        root = tree.getroot()
        self.body = root.find('.//body')

    def get_p_tags(self) -> None:
        """
        Extracts top-level paragraph elements from the body.
        """
        if self.body is None:
            raise ValueError("Body element not found. Ensure `get_body` is called first.")

        all_p_tags = self.body.findall('.//p')
        self.p_elements = [p for p in all_p_tags if self.is_top_level(p)]

    def is_top_level(self, node):
        """
        Determines if a paragraph is top-level in the XML tree.
        
        Args:
            node (ET.Element): Paragraph element.
        
        Returns:
            bool: True if top-level, False otherwise.
        """
        parent = node.find('..')
        return parent.tag == 'body' if parent is not None else False

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

    def mask_references_and_dates(self, element):
        """
        Masks references and dates, replacing them with placeholders.
        
        Args:
            element (ET.Element): The XML element to process.
        
        Returns:
            tuple: Modified element, masked references, and dates.
        """
        refs = self.mask_element_by_tag(element, 'ref')
        dates = self.mask_element_by_tag(element, 'date')
        return element, refs, dates

    def mask_element_by_tag(self, element, tag_name):
        """
        Masks elements of a given tag name, replacing with placeholders.
        
        Args:
            element (ET.Element): XML element to process.
            tag_name (str): Tag name to mask.
        
        Returns:
            list[str]: Masked elements.
        """
        masked = []
        for i, tag in enumerate(element.findall(f'.//{tag_name}')):
            placeholder = f"{self.celex}_{tag_name}_{i:02d}"
            original = tag.text or ""
            masked.append(f"{placeholder}: {original}")
            tag.text = placeholder
        return masked

    def unmask_element(self, sentences, refs, dates):
        """
        Replaces masked placeholders in sentences with original text.
        
        Args:
            sentences (list[str]): Sentences with placeholders.
            refs (list[str]): Masked references.
            dates (list[str]): Masked dates.
        
        Returns:
            list[str]: Sentences with restored text.
        """
        for idx, sentence in enumerate(sentences):
            for ref in refs:
                placeholder, content = ref.split(": ")
                sentence = sentence.replace(placeholder, content)
            for date in dates:
                placeholder, content = date.split(": ")
                sentence = sentence.replace(placeholder, content)
            sentences[idx] = re.sub(r'\s{2,}', ' ', sentence)
        return sentences

    def merge_dom_children(self, element):
        """
        Concatenates text content of an element and its children.
        
        Args:
            element (ET.Element): XML element.
        
        Returns:
            str: Merged text.
        """
        return "".join(element.itertext()).strip()

    def process_text(self, text):
        """
        Tokenizes text into sentences.
        
        Args:
            text (str): Text to tokenize.
        
        Returns:
            list[str]: List of sentences.
        """
        text = re.sub(r'\s{2,}', ' ', text)
        return text
