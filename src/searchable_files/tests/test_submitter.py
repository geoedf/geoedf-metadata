import os
from unittest import TestCase

from config import ROOT_DIR
from searchable_files.constants import INDEX_ID
from searchable_files.lib.search import app_search_client
from searchable_files.submitter import submit_handler
from searchable_files.watcher import watcher_handler


class Test(TestCase):
    def test_submit_handler(self):
        os.chdir(ROOT_DIR)

        # index_id = "073c72db-5791-47c9-8547-b605f2a6666a"
        index_id = INDEX_ID
        directory = "output/worker_metadata/assembled"
        submit_handler(directory, index_id)

    def test_watcher_handler(self):
        os.chdir(ROOT_DIR)

        task_id_file = "output/worker_metadata/submitted/tasks.txt"
        watcher_handler(task_id_file)

    def test_create_index(self):
        client = app_search_client()
        client.create_index("app_index", "This is an index created under the app's role")

    def test_get_index(self):
        client = app_search_client()
        response = client.get_index(INDEX_ID)
        return response

    def test_delete_subject(self):
        client = app_search_client()
        subject_id = ""
        client.delete_subject(INDEX_ID, subject_id)
