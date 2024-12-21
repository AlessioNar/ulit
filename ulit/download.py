import os
import io
import logging
import zipfile
import requests
from datetime import datetime
import json

# Constants
BASE_URL = 'http://publications.europa.eu/resource/cellar/'
ITA_URL = "https://www.normattiva.it/do/atto/caricaAKN?dataGU=20151216&codiceRedaz=15G00214&dataVigenza=20241218"
#ITA_URL = https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2017-04-24;050

def download_documents(results, download_dir, log_dir, format=None, source='cellar'):
    """
    Download documents in parallel using multiple threads.

    Sends a REST query to the specified source APIs and downloads the documents
    corresponding to the given results.

    Parameters
    ----------
    results : dict
        A dictionary containing the JSON results from the APIs.
    download_dir : str
        The directory where the downloaded documents will be saved.
    log_dir : str
        The directory where the logs will be saved.
    format : str, optional
        The format of the documents to download.
    source : str, optional
        The source of the documents ('cellar' or 'normattiva').

    Returns
    -------
    list
        A list of paths to the downloaded documents.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    if source == "cellar":
        cellar_ids = get_cellar_ids_from_json_results(cellar_results=results, format=format)
        document_paths = download_document(ids=cellar_ids, folder_path=os.path.join(download_dir), log_dir=log_dir, format=format)
        return document_paths
    elif source == "normattiva":
        document_paths = []
        for result in results:
            data_gu = result.get('dataGU', '20170424')
            codice_redaz = result.get('codiceRedaz', '17G00063')
            data_vigenza = result.get('dataVigenza', '20241210')
            response = fetch_content(f"https://www.normattiva.it/do/atto/caricaAKN?dataGU={data_gu}&codiceRedaz={codice_redaz}&dataVigenza={data_vigenza}")
            file_path = handle_response(response=response, folder_path=os.path.join(download_dir), cellar_id=f"{data_gu}_{codice_redaz}")
            document_paths.append(file_path)
        return document_paths
  


def get_cellar_ids_from_json_results(cellar_results, format):
    """
    Extract CELLAR ids from a JSON dictionary.

    Parameters
    ----------
    cellar_results : dict
        A dictionary containing the response of the CELLAR SPARQL query

    Returns
    -------
    list
        A list of CELLAR ids.

    Notes
    -----
    The function assumes that the JSON dictionary has the following structure:
    - The dictionary contains a key "results" that maps to another dictionary.
    - The inner dictionary contains a key "bindings" that maps to a list of dictionaries.
    - Each dictionary in the list contains a key "cellarURIs" that maps to a dictionary.
    - The innermost dictionary contains a key "value" that maps to a string representing the CELLAR URI.

    The function extracts the CELLAR id by splitting the CELLAR URI at "cellar/" and taking the second part.

    Examples
    --------
    >>> cellar_results = {
    ...     "results": {
    ...         "bindings": [
    ...             {"cellarURIs": {"value": "https://example.com/cellar/some_id"}},
    ...             {"cellarURIs": {"value": "https://example.com/cellar/another_id"}}
    ...         ]
    ...     }
    ... }
    >>> cellar_ids = get_cellar_ids_from_json_results(cellar_results)
    >>> print(cellar_ids)
    ['some_id', 'another_id']
    """
    cellar_uris = []
    results_list = cellar_results["results"]["bindings"]
    for i, file in enumerate(results_list):
        if file['format']['value'] == format:
            cellar_uris.append(file['cellarURIs']["value"].split("cellar/")[1])

    return cellar_uris

# Function to process a list of ids to download the corresponding zip files
def download_document(ids: list, folder_path: str, log_dir: str, format: str):
    """
    Process a list of ids to download the corresponding zip files.

    Parameters
    ----------
    ids : list
        List of ids to process.
    folder_path : str
        Path to the folder where the files will be downloaded.

    Returns
    -------
    None

    Raises
    ------
    Exception
        If an error occurs during the processing.

    Notes
    -----
    This function iterates over the list of ids, sends a GET request for each id,
    and downloads the corresponding file. If the file is a zip file, it is extracted
    to the specified folder. If the file is not a zip file, it is processed as a
    single file. If the file cannot be downloaded, the id is logged to a file.

    Examples
    --------
    >>> ids = ['id1', 'id2', 'id3']
    >>> folder_path = '/path/to/folder'
    >>> process_range(ids, folder_path)
    """
    try:
        file_paths = []
        
        for id in ids:
            print(id)
            response = fetch_content(BASE_URL + id)
            file_path = handle_response(response=response, folder_path=folder_path, cellar_id=id)
            file_paths.append(file_path)
        return file_paths

    except Exception as e:
        logging.error(f"Error processing range: {e}")


def handle_response(response, folder_path, cellar_id):
    """
    Handle a server response by saving or extracting its content.

    Parameters
    ----------
    response : requests.Response
        The HTTP response object.
    folder_path : str
        Directory where the file will be saved.
    cid : str
        CELLAR ID of the document.

    Returns
    -------
    str or None
        Path to the saved file or None if the response couldn't be processed.
    """
    content_type = response.headers.get('Content-Type', '')
    
    # The return file is usually either a zip file, or a file with the name DOC_* inside a folder named as the cellar_id
    target_path = os.path.join(folder_path, cellar_id)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    if 'zip' in content_type:
        extract_zip(response, target_path)
        return target_path
    else:
        extension = get_extension_from_content_type(content_type)
        if not extension:
            logging.warning(f"Unknown content type for ID {cellar_id}: {content_type}")
            return None

        file_path = f"{target_path}.{extension}"
        file_path = os.path.normpath(file_path)
        is_binary = 'text' not in content_type  # Assume binary if not explicitly text
        
        with open(file_path, mode='wb+') as f:
            f.write(response.content)            
        #print(response.content)
        #print(file_path)
        return file_path
    
def get_extension_from_content_type(content_type):
    """Map Content-Type to a file extension."""
    content_type_mapping = [
        'html',
        'json',
        'xml',
        'txt',
        'zip'
    ]
    for ext in content_type_mapping:
        if ext in content_type:
            return ext
    return None

def save_file(content, file_path, binary=False):
    """
    Save content to a file.

    Parameters
    ----------
    content : bytes or str
        The content to save.
    file_path : str
        Path to the file.
    binary : bool
        Whether the content is binary or text.
    """
    mode = 'wb' if binary else 'w'
    with open(file_path, mode) as f:
        f.write(content)


# Function to send a GET request to download a zip file for the given id under the CELLAR URI
def fetch_content(url) -> requests.Response:
    """
    Send a GET request to download a zip file for the given id under the CELLAR URI.

    Parameters
    ----------
    id : str
        The id of the resource to be retrieved.

    Returns
    -------
    requests.Response
        The response from the server.

    Notes
    -----
    The request is sent with the following headers:
    - Accept: application/zip;mtype=fmx4, application/xml;mtype=fmx4, application/xhtml+xml, text/html, text/html;type=simplified, application/msword, text/plain, application/xml;notice=object
    - Accept-Language: eng
    - Content-Type: application/x-www-form-urlencoded
    - Host: publications.europa.eu

    Raises
    ------
    requests.RequestException
        If there is an error sending the request.

    See Also
    --------
    requests : The underlying library used for making HTTP requests.

    Examples
    --------
    >>> import requests
    >>> response = rest_get_call('some_id')
    >>> if response is not None:
    ...     print(response.status_code)
    """
    try:
        url = url
        headers = {
            'Accept': "*, application/zip, application/zip;mtype=fmx4, application/xml;mtype=fmx4, application/xhtml+xml, text/html, text/html;type=simplified, application/msword, text/plain, application/xml, application/xml;notice=object",
            'Accept-Language': "eng",
            'Content-Type': "application/x-www-form-urlencoded",
            'Host': "publications.europa.eu"
        }
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logging.error(f"Error sending GET request: {e}")
        return None



# Function to get the current timestamp
def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


# Function to download a zip file and extract it
def extract_zip(response: requests.Response, folder_path: str):
    try:
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(folder_path)
    except Exception as e:
        logging.error(f"Error downloading zip: {e}")


# Main function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Simulate getting results from somewhere

    with open('./tests/metadata/query_results/query_results.json', 'r') as f:
        results = json.loads(f.read())  # Load the JSON data
    #document_paths = download_documents(results, './tests/data/html', log_dir='./tests/logs', format='xhtml')
    document_paths = download_documents(results, './tests/data/formex', log_dir='./tests/logs', format='fmx4')

    print(document_paths)