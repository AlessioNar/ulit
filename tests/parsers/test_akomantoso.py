import unittest
from op_cellar.parsers.akomantoso import AkomaNtosoParser
import os
import lxml.etree as etree

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
file_path = os.path.join(DATA_DIR, "32014L0092.akn")

class TestAkomaNtosoParser(unittest.TestCase):
 # Set maxDiff to None to ensure full diff is displayed for assertion failures
    maxDiff = None
    def setUp(self):
        self.parser = AkomaNtosoParser()

    def test_get_root(self):  

        # Verify file exists
        self.assertTrue(os.path.exists(file_path), f"Test file not found at {file_path}")

        # Get and verify root
        self.parser.get_root(file_path)
        self.assertIsNotNone(self.parser.root, "Root element should not be None")
               
    def test_get_meta_identification(self):
        self.parser.get_root(file_path)
        meta_identification = self.parser.get_meta_identification()
        
        self.assertIsNotNone(meta_identification)
        self.assertIn('work', meta_identification)
        self.assertEqual(meta_identification['work']['FRBRalias'], "32014L0092")

    def test_get_meta_references(self):
        self.parser.get_root(file_path)
        references = self.parser.get_meta_references()
        self.assertIsNotNone(references)
        self.assertEqual(references['eId'], "cirsfid")

    def test_get_meta_proprietary(self):
        self.parser.get_root(file_path)
        proprietary = self.parser.get_meta_proprietary()
        self.assertIsNotNone(proprietary)
        self.assertEqual(proprietary['file'], "L_2014257EN.01021401.doc.xml")

    def test_get_preface(self):

        self.parser.get_root(file_path)
        preface_text = self.parser.get_preface()
        self.assertIsNotNone(preface_text, "Preface element not found")
        
        # Validate the content of each paragraph
        self.assertEqual("Directive 2014/92/EU of the European Parliament and of the Council", preface_text[0],
                      "First paragraph text does not match expected content.")
        self.assertEqual("of 23 July 2014", preface_text[1], "Second paragraph text does not match expected content.")
        self.assertEqual("on the comparability of fees related to payment accounts, payment account switching and access to payment accounts with basic features", preface_text[2],
                      "Third paragraph text does not match expected content.")
        self.assertEqual("(Text with EEA relevance)", preface_text[3], "Fourth paragraph text does not match expected content.")
    
    def test_get_preamble(self):
        self.parser.get_root(file_path)

        preamble_data = self.parser.get_preamble()
        self.assertIsNotNone(preamble_data, "Preamble data not found")
    
    def test_get_preamble_formula(self):
        self.parser.get_root(file_path)
        formula_data = self.parser.get_preamble_formula()

        # Verify formula text
        self.assertIn("THE EUROPEAN PARLIAMENT AND THE COUNCIL OF THE EUROPEAN UNION", formula_data,
                      "Formula text in preamble does not match expected content")
        
    def test_get_preamble_citations(self):
        self.parser.get_root(file_path)
        citations_data = self.parser.get_preamble_citations()

        # Verify first citation content
        self.assertGreater(len(citations_data), 0, "No citations found in preamble")

        first_citation = citations_data[0]
        self.assertIn("Having regard to the Treaty on the Functioning of the European Union, and in particular Article 114", first_citation['citation_text'],
                      "First citation text does not match expected content")

        # Verify authorial note in fourth citation
        fourth_citation = citations_data[3]
        self.assertIn("OJ C 51, 22.2.2014, p. 3", fourth_citation['authorial_notes'][0],
                      "Expected authorial note text not found in fourth citation")

        # Verify date in the last citation's authorial note
        last_citation = citations_data[-1]
        self.assertIn("Position of the European Parliament of 15 April 2014", last_citation['authorial_notes'][0],
                      "Expected text in authorial note of last citation not found")
        
    def test_get_preamble_recitals(self):
        self.parser.get_root(file_path)

        recitals_data = self.parser.get_preamble_recitals()
        self.assertIsNotNone(recitals_data, "Recitals section not found in <preamble>")

        # Check the number of recitals extracted
        self.assertEqual(len(recitals_data), 59, "Incorrect number of recitals extracted")

        # Test first recital content
        intro_recital = recitals_data[0]
        self.assertEqual(intro_recital['eId'], "recs_1__intro_1", "Intro does not match expected value")
        self.assertEqual("Whereas:", 
                      intro_recital['recital_text'], "Intro recitals text does not match expected content")

        # Test second recital content with authorial note
        second_recital = recitals_data[2]
        self.assertEqual(second_recital['eId'], "recs_1__rec_(2)", "Second recital eId does not match expected value")
        self.assertEqual("In this respect, Directive 2007/64/EC of the European Parliament and of the Council established basic transparency requirements for fees charged by payment service providers in relation to services offered on payment accounts. This has substantially facilitated the activity of payment service providers, creating uniform rules with respect to the provision of payment services and the information to be provided, reduced the administrative burden and generated cost savings for payment service providers.", 
                      second_recital['recital_text'], "Second recital text does not match expected content")

        # Test third recital content
        third_recital = recitals_data[3]
        self.assertEqual(third_recital['eId'], "recs_1__rec_(3)", "Third recital eId does not match expected value")
        self.assertEqual("The smooth functioning of the internal market and the development of a modern, socially inclusive economy increasingly depends on the universal provision of payment services. Any new legislation in this regard must be part of a smart economic strategy for the Union, which must effectively take into account the needs of more vulnerable consumers.", 
                      third_recital['recital_text'], "Third recital text does not match expected content")

        # Test fourth recital content with date
        other_recital = recitals_data[16]
        self.assertEqual(other_recital['eId'], "recs_1__rec_(16)", "Sixteenth recital eId does not match expected value")
        self.assertEqual("Consumers would benefit most from information that is concise, standardised and easy to compare between different payment service providers. The tools made available to consumers to compare payment account offers would not have a positive impact if the time invested in going through lengthy lists of fees for different offers outweighed the benefit of choosing the offer that represents the best value. Those tools should be multifold and consumer testing should be conducted. At this stage, fee terminology should only be standardised for the most representative terms and definitions within Member States in order to avoid the risk of excessive information and to facilitate swift implementation.", 
                      other_recital['recital_text'], "Sixteenth recital text does not match expected content")

    def test_get_act(self):

        # Get and verify root
        self.parser.get_root(file_path)
        # Run get_act to set the `act` attribute
        self.parser.get_act()

        # Verify that `act` is an instance of etree._Element
        self.assertEqual(type(self.parser.act), etree._Element, "Act element should be an lxml.etree._Element")

        # Additional debug information if `act` is None
        if self.parser.act is None:
            print("No act element found. Available elements at root level:")
            for child in self.parser.root:
                print(f"- {child.tag}")

    def test_get_body(self):
        self.parser.get_root(file_path)
        # Test the get_body method
        self.parser.get_body()
        
        # Check if body is not None
        self.assertIsNotNone(self.parser.body, "Body element not found in the XML")
        # Check if `body` is an instance of etree._Element
        self.assertIsInstance(self.parser.body, etree._Element, "Body element should be an etree._Element")

        # More detailed assertion
        if self.parser.body is None:
            # Print available elements for debugging
            print("Available elements at root level:")
            for child in self.parser.root:
                print(f"- {child.tag}")
        
    def test_get_chapters(self):
        self.parser.get_root(file_path)
        self.parser.get_body()

        # Call get_chapters to populate self.chapters
        self.parser.get_chapters()
        print(self.parser.chapters)

        # Expected chapters data
        expected_chapters = [
            {'eId': 'chp_I', 'chapter_num': 'CHAPTER I', 'chapter_heading': 'SUBJECT MATTER, SCOPE AND DEFINITIONS'}, 
            {'eId': 'chp_II', 'chapter_num': 'CHAPTER II', 'chapter_heading': 'COMPARABILITY OF FEES CONNECTED WITH PAYMENT ACCOUNTS'}, 
            {'eId': 'chp_III', 'chapter_num': 'CHAPTER III', 'chapter_heading': 'SWITCHING'}, 
            {'eId': 'chp_IV', 'chapter_num': 'CHAPTER IV', 'chapter_heading': 'ACCESS TO PAYMENT ACCOUNTS'}, 
            {'eId': 'chp_V', 'chapter_num': 'CHAPTER V', 'chapter_heading': 'COMPETENT AUTHORITIES AND ALTERNATIVE DISPUTE RESOLUTION'}, 
            {'eId': 'chp_VI', 'chapter_num': 'CHAPTER VI', 'chapter_heading': 'SANCTIONS'}, 
            {'eId': 'chp_VII', 'chapter_num': 'CHAPTER VII', 'chapter_heading': 'FINAL PROVISIONS'}
        ]

        # Assert that self.chapters matches expected output
        self.assertEqual(self.parser.chapters, expected_chapters, "Chapters data does not match expected content")

if __name__ == '__main__':
    unittest.main()