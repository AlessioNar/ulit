import unittest
from ulit.parsers.formex import Formex4Parser
import xml.etree.ElementTree as ET

import os 

DATA_DIR = os.path.join(os.path.dirname(__file__), "..\\data\\formex")
file_path = os.path.join(DATA_DIR, "L_2011334EN.01002501.xml")

class TestFormex4Parser(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None  # Allow full diff if needed        
        self.parser = Formex4Parser()
        self.parser.get_root(file_path)

    def test_get_root(self):
        """Test parsing and root element retrieval from the Akoma Ntoso file."""
        self.assertTrue(os.path.exists(file_path), f"Test file not found at {file_path}")
        self.assertIsNotNone(self.parser.root, "Root element should not be None")
        
    def test_get_metadata(self):
        self.maxDiff = None  # Allow the full diff to be displayed
        
        self.parser.load_xml(file_path)

        result = self.parser.get_metadata()
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
    
    def test_get_preface(self):
        self.maxDiff = None  # Allow full diff if needed
    
    
        result = self.parser.get_preface()
        expected = (
            "Commission Implementing Regulation (EU) No 1319/2011 of 15 December 2011 "
            "fixing representative prices in the poultrymeat and egg sectors and for egg "
            "albumin, and amending Regulation (EC) No 1484/95"
        )
        self.assertEqual(self.parser.preface, expected)
    
    def test_get_preamble(self):
        """Test parsing the preamble section with quotations and numbered considerations in Formex4Parser."""
        self.maxDiff = None  # Allow full diff if needed
        
        result = self.parser.get_preamble()
        
        # Expected preamble structure
        # @todo - see main function
        expected = {
            "initial_statement": "THE EUROPEAN COMMISSION,",
            "quotations": [
                "Having regard to the Treaty on the Functioning of the European Union,",
                "Having regard to Council Regulation (EC) No 1234/2007 of 22 October 2007 establishing a common organisation of agricultural markets and on specific provisions for certain agricultural products (Single CMO Regulation)", # @incomplete
                "Having regard to Council Regulation (EC) No 614/2009 of 7 July 2009 on the common system of trade for ovalbumin and lactalbumin" # @incomplete
            ],
            "consid_init": "Whereas:",
            "considerations": [
                {"number": "(1)", "text": "Commission Regulation (EC) No 1484/95"}, # @incomplete
                {"number": "(2)", "text": "Regular monitoring of the data used to determine representative prices for poultrymeat and egg products and for egg albumin shows that the representative import prices for certain products should be amended to take account of variations in price according to origin. The representative prices should therefore be published."},
                {"number": "(3)", "text": "In view of the situation on the market, this amendment should be applied as soon as possible."},
                {"number": "(4)", "text": "The measures provided for in this Regulation are in accordance with the opinion of the Management Committee for the Common Organisation of Agricultural Markets,"}
            ],
            "preamble_final": "HAS ADOPTED THIS REGULATION:"
        }
        
        self.assertEqual(result, expected)
    
    def test_get_body(self):
        self.parser.get_body()
        self.assertIsNotNone(self.parser.body, "Body element should not be None")    
        
    def test_get_articles(self):
        self.parser.get_body()
        self.parser.get_articles()
        
        # Expected articles based on sample data in XML file
        expected = [
            {
                "eId": "001",
                "article_num": "Article 1",
                "article_text": "Annex I to Regulation (EC) No 1484/95 is replaced by the Annex to this Regulation."
            },
            {
                "eId": "002",
                "article_num": "Article 2",
                "article_text": "This Regulation shall enter into force on the day of its publication in the Official Journal of the European Union."
            }
        ]
        
        self.assertEqual(self.parser.articles, expected)

# Run the tests
if __name__ == "__main__":
    unittest.main()
