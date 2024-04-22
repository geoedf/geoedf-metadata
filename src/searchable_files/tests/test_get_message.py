import json
import os
import uuid
from unittest import TestCase

from get_message import callback, get_task_id


class TestExtraction(TestCase):
    def test_callback(self):
        """
            Message Examples:
            {
                "uuid": str(uuid.uuid4()),
                "publication_name": "gds_test_shp",
                "path": "data/files/public/idata_files/AT15-51.shp",
                "type": "single"
            }
        """
        project_dir = os.path.abspath(os.path.join(os.getcwd(), '../../..'))
        os.chdir(project_dir)

        mock_msg = {
            "uuid": str(uuid.uuid4()),
            "user_id": "qu112@purdue.edu",
            "publication_name": "bogota data test",
            "path": "data/files/single_file/bogota.tif",
            # "path": "staging/20240311085013",
            "type": "single",
            "description": "This is the description of a resource published from GeoEDF Publish Wizard. (Test)",
            "keywords": ["111", "222"],  # todo
            "publication_type": "Geospatial Files",
        }
        mock_body = json.dumps(mock_msg, indent=4)
        mock_body = mock_body.encode()
        callback(None, None, None, mock_body)

    def test_get_task_id(self):
        task_id_file = "output/worker_metadata/submitted/tasks.txt"
        task_id = get_task_id(task_id_file)
        print(task_id)
        self.assertIsNotNone(task_id)
