import unittest
from op_cellar.parser.parser import HTMLParser, Formex4Parser, AkomaNtosoParser
import xml.etree.ElementTree as ET

import os 

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

class TestFormex4Parser(unittest.TestCase):
    def setUp(self):
        self.formex_parser = Formex4Parser()

    def test_parse_metadata(self):
        self.maxDiff = None  # Allow the full diff to be displayed
        file_path = os.path.join(DATA_DIR, "L_2011334EN.01002501.xml")
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ET.parse(f)
            root = tree.getroot()
        result = self.formex_parser._parse_metadata(root)
        expected = {
            "file": "L_2011334EN.01002501.doc.xml",
            "collection": "L",
            "oj_number": "334",
            "year": "2011",
            "language": "EN",
            "page_first": "25",
            "page_seq": "1",
            "document_language": "EN",
            "sequence_number": "0009",
            "total_pages": "1",
            "volume_ref": "01",
            "doc_format": "NY",
            "doc_type": "OJ",
            "doc_number": "1319"
        }
        self.assertEqual(result, expected)
    
    def test_parse_title(self):
        self.maxDiff = None  # Allow full diff if needed
        file_path = os.path.join(DATA_DIR, "L_2011334EN.01002501.xml")
        
        # Parse the XML tree and pass the root to _parse_title
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ET.parse(f)
            root = tree.getroot()
        
        result = self.formex_parser._parse_title(root)
        expected = (
            "Commission Implementing Regulation (EU) No 1319/2011 of 15 December 2011 "
            "fixing representative prices in the poultrymeat and egg sectors and for egg "
            "albumin, and amending Regulation (EC) No 1484/95"
        )
        self.assertEqual(result, expected)
    
    def test_parse_preamble(self):
        self.maxDiff = None  # Allow full diff if needed
        file_path = os.path.join(DATA_DIR, "L_2011334EN.01002501.xml")
        
        # Parse the XML tree and pass the root to _parse_preamble
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ET.parse(f)
            root = tree.getroot()
        
        result = self.formex_parser._parse_preamble(root)
        
        # Expected preamble based on sample data in XML file
        expected = {
            "initial_statement": "THE EUROPEAN COMMISSION,",
            "considerations": [
                "Commission Regulation (EC) No 1484/95",
                "Regular monitoring of the data used to determine representative prices for poultrymeat and egg products and for egg albumin shows that the representative import prices for certain products should be amended to take account of variations in price according to origin. The representative prices should therefore be published.",
                "In view of the situation on the market, this amendment should be applied as soon as possible.",
                "The measures provided for in this Regulation are in accordance with the opinion of the Management Committee for the Common Organisation of Agricultural Markets,"
            ]
        }
        
        self.assertEqual(result, expected)



       


# Run the tests
if __name__ == "__main__":
    unittest.main()
