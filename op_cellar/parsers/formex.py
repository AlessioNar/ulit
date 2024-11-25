from .parser import Parser
import re
from lxml import etree
from collections import OrderedDict
import re
from datetime import date

from lxml import etree, objectify
from lxml.builder import ElementMaker


# Create a new objectify parser that doesn't remove blank text nodes
objectify_parser = etree.XMLParser()
objectify_parser.set_element_class_lookup(objectify.ObjectifyElementClassLookup())

FMX_NAMESPACES = {
            'fmx': 'http://formex.publications.europa.eu/schema/formex-05.56-20160701.xd'
        }

class AkomaNtosoDocument():
    """ Base class for Akoma Ntoso documents.

    :ivar root: :class:`lxml.objectify.ObjectifiedElement` root of the XML document
    :ivar namespace: primary XML namespace
    """
    _parser = objectify_parser
    # the "source" attribute used on some elements where it is required.
    # contains: name, id, url
    source = ["cobalt", "cobalt", "https://github.com/laws-africa/cobalt"]

    def __init__(self, xml=None):
        if isinstance(xml, str):
            xml = xml.encode('utf-8')
        self.parse(xml)
        self.maker = objectify.ElementMaker(annotate=False, namespace=self.namespace, nsmap=self.root.nsmap)

    def parse(self, xml, document_type=None):
        """ Parse XML and ensure it's Akoma Ntoso with a known namespace. Raises ValueError on error.
        """
        self.root = objectify.fromstring(xml, parser=self._parser)

        # ensure the root element is correct
        name = self.root.tag.split('}', 1)[-1]
        if name != 'akomaNtoso':
            raise ValueError(f"XML root element must be akomaNtoso, but got {name} instead")

        self.namespace = self.get_namespace()

    def to_xml(self, *args, encoding='utf-8', **kwargs):
        return etree.tostring(self.root, *args, encoding=encoding, **kwargs)

    def get_namespace(self):
        akn_namespaces = [ns[1] for ns in sorted(list(FMX_NAMESPACES.items()), reverse=True)]
        namespaces = list(self.root.nsmap.values())
        for ns in akn_namespaces:
            if ns in namespaces:
                return ns

        raise ValueError(f"Expected to find one of the following Akoma Ntoso XML namespaces: {', '.join(akn_namespaces)}. Only these namespaces were found: {', '.join(namespaces)}")

    def ensure_element(self, name, after, at=None, attribs=None):
        """ Helper to get an element if it exists, or create it if it doesn't.

        :param name: dotted path from `self` or `at`
        :param after: element after which to place the new element if it doesn't exist
        :param at: element at which to start looking, (defaults to self if None)
        """
        node = self.get_element(name, root=at)
        if node is None:
            # TODO: what if nodes in the path don't exist?
            node = self.make_element(name.split('.')[-1], attribs)
            after.addnext(node)

        return node

    def get_element(self, name, root=None):
        """ Lookup a dotted-path element, start at root (or self if root is None). Returns None if the element doesn't exist.
        """
        parts = name.split('.')
        # this avoids an lxml warning about testing against None
        if root is not None:
            node = root
        else:
            node = self

        for p in parts:
            try:
                node = getattr(node, p)
            except AttributeError:
                return None
        return node

    def make_element(self, elem, attribs=None):
        attribs = attribs or {}
        return getattr(self.maker, elem)(**attribs)

class Formex4Parser(Parser):
    def __init__(self):
        """
        Initializes the parser
        
        """
        # Define the namespace mapping
        self.namespaces = FMX_NAMESPACES

            
    def load_xml(self, file):
        """
        """
        with open(file, 'r', encoding='utf-8') as f:
            tree = etree.parse(f)
            self.root = tree.getroot()

    def get_metadata(self):
        """
        Extracts metadata information from the BIB.INSTANCE section.

        Args:
        root (Element): Root XML element.

        Returns:
        dict: Extracted metadata.
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

    def get_title(self, root):
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
        
    def get_preamble(self, root):
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
    

    def get_articles(self):
        """
        Extracts articles from the ENACTING.TERMS section.

        Args:
        root (Element): Root XML element.

        Returns:
        list: Articles with identifier and content.
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

        Returns:
        dict: Parsed data containing metadata, title, preamble, and articles.
        """
        self.load_xml(file)
        self.get_body()
        self.get_articles()