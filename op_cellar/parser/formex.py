from .parser import Parser
import re
import xml.etree.ElementTree as ET

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
