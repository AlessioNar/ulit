import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from tulit.sparql import send_sparql_query, get_results_table
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "./metadata/queries")

class TestSendSparqlQuery(unittest.TestCase):
    def setUp(self):
        self.sparql_query_filepath = ""
        
    def test_send_sparql_query(self):
        
        self.maxDiff = None  # Allow the full diff to be displayed
        sparql_file_path = os.path.join(DATA_DIR, "formex_query.rq")
        celex = "32024R0903"
        # Send query
        response = send_sparql_query(sparql_query_filepath=sparql_file_path, celex=celex)
        #print(response)
        expected_results = json.loads('''{"head": {"link": [], "vars": ["cellarURIs", "manif", "format", "expr"]}, "results": {"distinct": false, "ordered": true, "bindings": [{"cellarURIs": {"type": "uri", "value": "http://publications.europa.eu/resource/cellar/c008bcb6-e7ec-11ee-9ea8-01aa75ed71a1.0006.02/DOC_1"}, "manif": {"type": "uri", "value": "http://publications.europa.eu/resource/cellar/c008bcb6-e7ec-11ee-9ea8-01aa75ed71a1.0006.02"}, "format": {"type": "typed-literal", "datatype": "http://www.w3.org/2001/XMLSchema#string", "value": "fmx4"}, "expr": {"type": "uri", "value": "http://publications.europa.eu/resource/cellar/c008bcb6-e7ec-11ee-9ea8-01aa75ed71a1.0006"}}]}}''')
        #print(expected_results)
        self.assertEqual(response, expected_results)

if __name__ == "__main__":
    unittest.main()
