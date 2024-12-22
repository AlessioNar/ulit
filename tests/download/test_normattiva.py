import unittest
import json
from ulit.download.cellar import CellarDownloader
import os
from unittest.mock import patch, Mock
import requests
import io

class TestNormattivaDownloader(unittest.TestCase):
    def test_download_normattiva(self):
        dummy = ''
        #download_documents(dummy, './tests/data/formex', log_dir='./tests/logs', format='fmx4', source='normattiva')

