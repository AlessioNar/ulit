import os
import io
import logging
import zipfile
import requests
from datetime import datetime
import threading
import json

# Constants
BASE_URL = 'http://publications.europa.eu/resource/cellar/'
LOG_DIR = 'logs/'

def download_documents(results, download_dir, nthreads=1):
    """
    Download Cellar documents in parallel using multiple threads.

    Sends a REST query to the Publications Office APIs and downloads the documents
    corresponding to the given results.

    Parameters
    ----------
    results : dict
        A dictionary containing the JSON results from the Publications Office APIs.
    download_dir : str
        The directory where the downloaded documents will be saved.
    nthreads : int
        The number of threads to use to make the request

    Notes
    -----
    The function uses a separate thread for each subset of Cellar ids.
    The number of threads can be adjusted by modifying the `nthreads` parameter.
    """
    cellar_ids = get_cellar_ids_from_json_results(results)

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    threads = []
    for i in range(nthreads):  
        cellar_ids_subset = cellar_ids[i::nthreads]
        print(cellar_ids_subset)
        t = threading.Thread(target=process_range, args=(cellar_ids_subset, os.path.join(download_dir)))
        threads.append(t)
    [t.start() for t in threads]
    [t.join() for t in threads]

def get_cellar_ids_from_json_results(cellar_results):
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
    results_list = cellar_results["results"]["bindings"]
    cellar_ids_list = [results_list[i]["cellarURIs"]["value"].split("cellar/")[1] for i in range(len(results_list))]
    return cellar_ids_list

# Function to process a list of ids to download the corresponding zip files
def process_range(ids: list, folder_path: str):
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
        zip_files = []
        single_files = []
        other_downloads = []
        
        for id in ids:
            sub_folder_path = os.path.join(folder_path, id)
            
            response = rest_get_call(id.strip())
            if response is None:
                continue
            
            if 'Content-Type' in response.headers:
                if 'zip' in response.headers['Content-Type']:
                    zip_files.append(id)
                    extract_zip(response, sub_folder_path)
                else:
                    single_files.append(id)
                    process_single_file(response, sub_folder_path)
            else:
                other_downloads.append(id)
        
        if len(other_downloads) != 0:
            # Log results
            id_logs_path = LOG_DIR + 'failed_' + get_current_timestamp() + '.txt'
            os.makedirs(os.path.dirname(id_logs_path), exist_ok=True)
            with open(id_logs_path, 'w+') as f:
                f.write('Failed downloads ' + get_current_timestamp() + '\n' + str(other_downloads))
        
        with open(LOG_DIR + get_current_timestamp() + '.txt', 'w+') as f:
            f.write(f"Zip files: {len(zip_files)}, Single files: {len(single_files)}, Failed downloads: {len(other_downloads)}")
    except Exception as e:
        logging.error(f"Error processing range: {e}")

# Function to send a GET request to download a zip file for the given id under the CELLAR URI
def rest_get_call(id: str) -> requests.Response:
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
    - Accept: application/xhtml+xml @todo - cater for other kinds of requests too.
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
        url = BASE_URL + id
        headers = {
            'Accept': "application/zip;mtype=fmx4, application/xml;mtype=fmx4, application/xhtml+xml, text/html, text/html;type=simplified, application/msword, text/plain, application/xml;notice=object",
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


# Function to process a single file
def process_single_file(response: requests.Response, folder_path: str):
    """
    Process a single file by saving its contents to a file.

    Parameters
    ----------
    response : requests.Response
        The HTTP response object containing the file contents.
    folder_path : str
        The path to the folder where the file will be saved.

    Returns
    -------
    None

    Notes
    -----
    This function saves the contents of a single file from an HTTP response to a
    file on disk. The file name is constructed by appending the id to the folder
    path with an '.html' extension. The function ensures that the directory path
    exists before attempting to write the file.

    Examples
    --------
    >>> response = requests.get('http://example.com/file')
    >>> folder_path = '/path/to/folder'
    >>> process_single_file(response, folder_path)
    """
    out_file = folder_path + '.html'
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w+', encoding="utf-8") as f:
        f.write(response.text)



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

# Function to log downloaded files
def log_downloaded_files(downloaded_files: list, dir_to_check: str):
    in_dir_name = LOG_DIR + 'in_dir_lists/'
    os.makedirs(os.path.dirname(in_dir_name), exist_ok=True)
    print_list_to_file(in_dir_name + 'in_dir_' + get_current_timestamp() + '.txt', downloaded_files)

# Function to log missing ids
def log_missing_ids(missing_ids: list):
    new_ids_dir_name = LOG_DIR + 'cellar_ids/'
    os.makedirs(os.path.dirname(new_ids_dir_name), exist_ok=True)
    print_list_to_file(new_ids_dir_name + 'cellar_ids_' + get_current_timestamp() + '.txt', missing_ids)


# Function to print a list to a file
def print_list_to_file(filename, lst):
    with open(filename, 'w+') as f:
        for item in lst:
            f.write(item + '\n')


# Main function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Simulate getting results from somewhere
    with open('results.json', 'r') as f:
        results = json.loads(f.read())  # Load the JSON data
    download_documents(results, './downloads')