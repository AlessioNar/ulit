import os
import io
import logging
import zipfile
import requests

class DocumentDownloader:
    """	
    A generic document downloader class.
    """	
    def __init__(self, download_dir, log_dir):
        self.download_dir = download_dir
        self.log_dir = log_dir
        self._ensure_directories()

    def _ensure_directories(self):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def handle_response(self, response, cellar_id):
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
        target_path = os.path.join(self.download_dir, cellar_id)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        if 'zip' in content_type:
            self.extract_zip(response, target_path)
            return target_path
        else:
            extension = self.get_extension_from_content_type(content_type)
            if not extension:
                logging.warning(f"Unknown content type for ID {cellar_id}: {content_type}")
                return None

            file_path = f"{target_path}.{extension}"
            file_path = os.path.normpath(file_path)
            
            with open(file_path, mode='wb+') as f:
                f.write(response.content)            
                
            return file_path
        
    def get_extension_from_content_type(self, content_type):
        """Map Content-Type to a file extension."""
        content_type_mapping = {
            'text/html': 'html',
            'application/json': 'json',
            'application/xml': 'xml',
            'text/plain': 'txt',
            'application/zip': 'zip',
            'text/xml': 'xml',
        }
        for ext, mapped_ext in content_type_mapping.items():
            if ext in content_type:
                return mapped_ext

    # Function to download a zip file and extract it
    def extract_zip(self, response: requests.Response, folder_path: str):
        try:
            z = zipfile.ZipFile(io.BytesIO(response.content))
            z.extractall(folder_path)
        except Exception as e:
            logging.error(f"Error downloading zip: {e}")

