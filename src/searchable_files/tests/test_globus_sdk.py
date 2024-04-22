import os
from unittest import TestCase

from config import ROOT_DIR
from searchable_files.constants import INDEX_ID
from searchable_files.lib.search import app_search_client


class TestGlobusSDK(TestCase):
    def setUp(self):
        self.original_dir = os.getcwd()
        os.chdir(ROOT_DIR)

        self.client = app_search_client()

    def tearDown(self):
        os.chdir(self.original_dir)

    def test_create_index(self):
        self.client.create_index("app_index", "This is an index created under the app's role")

    def test_get_index(self):
        response = self.client.get_index(INDEX_ID)
        return response

    def test_delete_subject(self):
        subject_id = "4abb6e4b-73f3-4bdb-bad1-28ca05088423"
        self.client.delete_subject(INDEX_ID, subject_id)
