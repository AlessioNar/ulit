import unittest
import json
from ulit.download import download_documents
import os


class TestDownload(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
                
    def test_download_documents(self):
            
        # Send query
        with open('./tests/metadata/query_results/query_results.json', 'r') as f:
            results = json.loads(f.read())  # Load the JSON data        
        document_paths = download_documents(results, './tests/data/formex', log_dir='./tests/logs', format='fmx4', source='cellar')

        expected = [
            'tests\\data\\formex\\e115172d-3ab3-4b14-b0a4-dfdcc9871793.0006.04\\DOC_1.xml', 'tests\\data\\formex\\e115172d-3ab3-4b14-b0a4-dfdcc9871793.0006.04\\DOC_2.xml', 'tests\\data\\formex\\e115172d-3ab3-4b14-b0a4-dfdcc9871793.0006.04\\DOC_3.xml', 'tests\\data\\formex\\e115172d-3ab3-4b14-b0a4-dfdcc9871793.0006.04\\DOC_4.xml'
        ]
        self.assertEqual(document_paths, expected)
        
    def test_download_normattiva(self):
        dummy = ''
        download_documents(dummy, './tests/data/formex', log_dir='./tests/logs', format='fmx4', source='normattiva')


if __name__ == "__main__":
    unittest.main()