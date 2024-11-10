import unittest
from op_cellar.parsers.parser import validate_xml
import os 

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestXMLValidator(unittest.TestCase):
    def setUp(self):
        """Set up test paths."""

        # Update these paths to match your actual file locations
        self.valid_xml = os.path.join(DATA_DIR, "32014L0092.akn")
        #self.invalid_xml = "path/to/invalid.xml"
        self.xsd_file = os.path.join(DATA_DIR, "schemas", "akomantoso30.xsd")

#    def test_valid_xml(self):
#        """Test validation with valid XML file."""
#        is_valid, error = validate_xml(self.valid_xml, self.xsd_file)
#        self.assertTrue(is_valid)
#        self.assertIsNone(error)

#    def test_invalid_xml(self):
#        """Test validation with invalid XML file."""
#        is_valid, error = validate_xml_against_xsd(self.invalid_xml, self.xsd_file)
#        self.assertFalse(is_valid)
#        self.assertIsNotNone(error)

#    def test_nonexistent_xml_file(self):
#        """Test validation with non-existent XML file."""
#        is_valid, error = validate_xml("data/nonexistent.xml", self.xsd_file)
#        self.assertFalse(is_valid)
#        self.assertIsNotNone(error)

#    def test_nonexistent_xsd_file(self):
#        """Test validation with non-existent XSD schema file."""
#        is_valid, error = validate_xml(self.valid_xml, "nonexistent.xsd")
#        self.assertFalse(is_valid)
#        self.assertIsNotNone(error)

if __name__ == '__main__':
    unittest.main(verbosity=2)