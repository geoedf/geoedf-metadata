from unittest import TestCase

from searchable_files.submitter import submit_handler


class Test(TestCase):
    def test_submit_handler(self):
        index_id = "76c5e7eb-6cb6-492c-ba80-7e47abff0586"
        directory = "output/worker_metadata/assemble"
        submit_handler(directory, index_id)
