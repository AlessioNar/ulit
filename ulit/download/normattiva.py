from download import DocumentDownloader
import requests
import logging

class NormattivaDownloader(DocumentDownloader):
    def __init__(self, download_dir, log_dir):
        super().__init__(download_dir, log_dir)
        self.endpoint = "https://www.normattiva.it/do/atto/caricaAKN?dataGU=20151216&codiceRedaz=15G00214&dataVigenza=20241218"
    
    def build_request_url(self, params=None) -> str:
        """
        Build the request URL based on the source and parameters.
        """
        uri = f"https://www.normattiva.it/eli/id/{params['date']}//{params['codiceRedaz']}/CONSOLIDATED"
        #uri = f"https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:{params['date']};{params['number']}"
        url = f"https://www.normattiva.it/do/atto/caricaAKN?dataGU={params['dataGU']}&codiceRedaz={params['codiceRedaz']}&dataVigenza={params['dataVigenza']}"
        
        return uri, url
                    
    def fetch_content(self, uri, url) -> requests.Response:
        """
        Send a GET request to download a file

        Parameters
        ----------
        url : str
            The URL to send the request to.

        Returns
        -------
        requests.Response
            The response from the server.

        Raises
        ------
        requests.RequestException
            If there is an error sending the request.
        """
        try:
            
            # Make a GET request to the URI to get the cookies        
            cookies_response = requests.get(uri)
            cookies_response.raise_for_status()
            cookies = cookies_response.cookies
            print(cookies)
            headers = {
                'Accept': "text/xml",
                'Accept-Encoding': "gzip, deflate, br, zstd",
                'Accept-Language': "en-US,en;q=0.9",
                
            }                     
            response = requests.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Error sending GET request: {e}")
            return None
             
        
        
    def download(self, dataGU, codiceRedaz, dataVigenza, date):     
        document_paths = []
        params = {
            'dataGU': dataGU,
            'codiceRedaz': codiceRedaz,
            'dataVigenza': dataVigenza,
            'date': date,
            #'number': number
        }
        uri, url = self.build_request_url(params)
        
        response = self.fetch_content(uri, url)
        file_path = self.handle_response(response=response, cellar_id=params['codiceRedaz'])
        document_paths.append(file_path)
        return document_paths

# Example usage
if __name__ == "__main__":
    downloader = NormattivaDownloader(download_dir='./tests/data/akn/italy', log_dir='./tests/logs')
    documents = downloader.download(dataGU='20150716', codiceRedaz='15G00122', dataVigenza='20241218', date='2015/07/16')
    
    print(documents)
    