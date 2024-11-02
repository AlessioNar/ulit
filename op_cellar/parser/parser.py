from abc import ABC, abstractmethod
import re
from http.server import BaseHTTPRequestHandler
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

class Parser(ABC):
    @abstractmethod
    def parse(self, data):
        pass

class HTMLParser(Parser):
    def parse(self, file, granularity='article'):
        """
        Parses the HTML content of a file at a specified level of granularity.

        Args:
        file (str): Path to the HTML file.
        granularity (str): The level of granularity for extraction, such as 'article' or 'paragraph'.

        Returns:
        dict: Extracted text organized by HTML element IDs.
        """
        with open(file, 'r', encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        
        if granularity == 'article':
            articles = soup.find_all('div', class_='eli-subdivision', id=lambda x: x and x.startswith('art_'))
            article_text = {}
            for article in articles:
                text = article.get_text()
                text = text.encode('ascii', 'ignore').decode('ascii')
                text = re.sub(r'\s+', ' ', text).strip()
                article_text[article['id']] = text
            return article_text
        
        elif granularity == 'paragraph':
            enacting_terms = soup.find('div', class_='eli-subdivision', id='enc_1')
            if not enacting_terms:
                raise ValueError("No enacting terms found with ID 'enc_1'.")

            paragraphs = enacting_terms.find_all(
                'div',
                id=lambda x: x and len(x.split('.')) == 2 and len(x.split('.')[0]) == 3 and len(x.split('.')[1]) == 3
            )

            paragraph_text = {}
            for paragraph in paragraphs:
                text = paragraph.get_text()
                text = text.encode('ascii', 'ignore').decode('ascii')
                text = re.sub(r'\s+', ' ', text).strip()
                paragraph_text[paragraph['id']] = text
            
            # Handle paragraphs in nested lists or other sub-divisions
            for article in soup.find_all('div', class_='eli-subdivision', id=lambda x: x and x.startswith('art_')):
                lists = article.find_all(['ul', 'ol'])
                for list_item in lists:
                    list_paragraphs = list_item.find_all('div', id=True)
                    for para in list_paragraphs:
                        text = para.get_text()
                        text = text.encode('ascii', 'ignore').decode('ascii')
                        text = re.sub(r'\s+', ' ', text).strip()
                        paragraph_text[para['id']] = text

            return paragraph_text

        else:
            raise ValueError(f"Unsupported granularity: {granularity}")

class XMLParser(Parser):
    def parse(self, data):
        # Your XML parsing logic here
        pass

class Formex4Parser(Parser):
    def parse(self, file):
        """
        Parses a FORMEX XML document to extract metadata, title, preamble, and enacting terms.

        Args:
        file (str): Path to the FORMEX XML file.

        Returns:
        dict: Parsed data containing metadata, title, preamble, and articles.
        """
        with open(file, 'r', encoding='utf-8') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            
                        
        parsed_data = {
            "metadata": self._parse_metadata(root),
            "title": self._parse_title(root),
            "preamble": self._parse_preamble(root),
            "articles": self._parse_articles(root),
        }

        return parsed_data

    def _parse_metadata(self, root):
        """
        Extracts metadata information from the BIB.INSTANCE section.

        Args:
        root (Element): Root XML element.

        Returns:
        dict: Extracted metadata.
        """
        metadata = {}
        bib_instance = root.find('BIB.INSTANCE')
        
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

    def _parse_title(self, root):
        """
        Extracts title information from the TITLE section.

        Args:
        root (Element): Root XML element.

        Returns:
        str: Concatenated title text.
        """
        title_element = root.find('TITLE')
        title_text = ""
        
        if title_element is not None:
            for paragraph in title_element.iter('P'):
                paragraph_text = "".join(paragraph.itertext()).strip()
                title_text += paragraph_text + " "
        
        return title_text.strip()
    
    
    def _parse_preamble(self, root):
        """
        Extracts the preamble section, including initial statements and considerations.

        Args:
            root (Element): Root XML element.

        Returns:
            dict: Preamble details, including quotations and considerations.
        """
        preamble_data = {"initial_statement": None, "quotations": [], "consid_init": None, "considerations": [], "preamble_final": None}
        preamble = root.find('PREAMBLE')

        if preamble is not None:
            # Initial statement
            preamble_data["initial_statement"] = preamble.findtext('PREAMBLE.INIT')
            
            # Removing NOTE tags as they produce noise
            notes = preamble.findall('.//NOTE')
            for note in notes:
                for parent in preamble.iter():
                    if note in list(parent):
                        parent.remove(note)
            # @todo. In this way we also lose the tail of each XML node NOTE that we remove. This should not happen.

            
            # Extract each <VISA> element's text in <GR.VISA>
            for visa in preamble.findall('.//VISA'):
                text = "".join(visa.itertext()).strip()  # Using itertext() to get all nested text
                text = text.replace('\n', '').replace('\t', '').replace('\r', '')  # remove newline and tab characters
                text = re.sub(' +', ' ', text)  # replace multiple spaces with a single space
                preamble_data["quotations"].append(text)

            preamble_data["consid_init"] = preamble.findtext('.//GR.CONSID/GR.CONSID.INIT')

            # Extract each <TXT> element's text and corresponding <NO.P> number within <CONSID>
            for consid in preamble.findall('.//CONSID'):
                number = consid.findtext('.//NO.P')
                text = "".join(consid.find('.//TXT').itertext()).strip()
                preamble_data["considerations"].append({"number": number, "text": text})

            preamble_data["preamble_final"] = preamble.findtext('PREAMBLE.FINAL')

        
        return preamble_data


    def _parse_articles(self, root):
        """
        Extracts articles from the ENACTING.TERMS section.

        Args:
        root (Element): Root XML element.

        Returns:
        list: Articles with identifier and content.
        """
        articles = []
        enacting_terms = root.find('ENACTING.TERMS')
        
        if enacting_terms is not None:
            for article in enacting_terms.findall('ARTICLE'):
                article_data = {
                    "identifier": article.get("IDENTIFIER"),
                    "title": article.findtext('TI.ART'),
                    "content": " ".join("".join(alinea.itertext()).strip() for alinea in article.findall('ALINEA'))
                }
                articles.append(article_data)
        
        return articles

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
