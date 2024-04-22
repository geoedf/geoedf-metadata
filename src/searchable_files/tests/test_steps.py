import os
from unittest import TestCase

from config import ROOT_DIR
from searchable_files.assembler import assemble_handler
from searchable_files.constants import INDEX_ID
from searchable_files.extractor import extract_handler
from searchable_files.lib.search import app_search_client
from searchable_files.submitter import submit_handler
from searchable_files.watcher import watcher_handler
import uuid


class Test(TestCase):
    def setUp(self):
        self.original_dir = os.getcwd()
        os.chdir(ROOT_DIR)

        self.client = app_search_client()

    def tearDown(self):
        os.chdir(self.original_dir)

    def test_extract_handler(self):
        resource_uuid = str(uuid.uuid4())
        publication_description = "This publication is a resource in GeoEDF Portal. (Test)"
        extract_handler(resource_uuid, "Test FAIR", "data/files/jupyter/test1/",
                        True, "multiple", publication_description, "kw1")
        # extract_handler(resource_uuid, "Test FAIR", "data/files/public/idata_files/maize_YieldPerHectare.tif",
        #                 True, "single", "This publication is a resource in GeoEDF Portal. (Test)", "kw1")

    def test_assemble_handler(self):
        assemble_handler("output/worker_metadata/extracted", True)

    def test_submit_handler(self):
        index_id = INDEX_ID
        directory = "output/worker_metadata/assembled"
        submit_handler(directory, index_id)

    def test_watcher_handler(self):
        task_id_file = "output/worker_metadata/submitted/tasks.txt"
        watcher_handler(task_id_file)

    def test_create_index(self):
        self.client.create_index("app_index", "This is an index created under the app's role")

    def test_get_index(self):
        response = self.client.get_index(INDEX_ID)
        return response

    def test_delete_subject(self):
        subject_id = "4abb6e4b-73f3-4bdb-bad1-28ca05088423"
        self.client.delete_subject(INDEX_ID, subject_id)
