import os
import io
import logging
import zipfile
import requests
from datetime import datetime
import json
from download import DocumentDownloader

# Constants
ITA_URL = "https://www.normattiva.it/do/atto/caricaAKN?dataGU=20151216&codiceRedaz=15G00214&dataVigenza=20241218"


class NormattivaDownloader(DocumentDownloader):
    def __init__(self, download_dir, log_dir):
        super().__init__(download_dir, log_dir)
    
    def build_request_url(self, source, params):
        """
        Build the request URL based on the source and parameters.
        """
        
        return f"https://www.normattiva.it/do/atto/caricaAKN?dataGU={params['date']}&codiceRedaz={params['codiceRedaz']}&dataVigenza={params['dataVigenza']}"
        
    
    def download_document(self, url, format):     
        document_paths = []
        result = {
            'dataGU': '20151216',
            'codiceRedaz': '15G00214',
            'dataVigenza': '20241218'
        }
        data_gu = result.get('dataGU', '20170424')
        codice_redaz = result.get('codiceRedaz', '17G00063')
        data_vigenza = result.get('dataVigenza', '20241210')
        response = self.fetch_content(f"https://www.normattiva.it/do/atto/caricaAKN?dataGU={data_gu}&codiceRedaz={codice_redaz}&dataVigenza={data_vigenza}")
        file_path = self.handle_response(response=response)
        document_paths.append(file_path)
        return document_paths

    
# Example usage
if __name__ == "__main__":
    downloader = NormattivaDownloader(download_dir='./tests/data/formex', log_dir='./tests/logs')
    url = "https://www.normattiva.it/do/atto/caricaAKN?dataGU=20151216&codiceRedaz=15G00214&dataVigenza=20241218"
    documents = downloader.download(url)
    
    print(documents)
    