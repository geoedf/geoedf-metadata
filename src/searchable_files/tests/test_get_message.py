import json
import os
import uuid
from unittest import TestCase

from get_message import callback


class Test(TestCase):
    def test_callback(self):
        project_dir = os.path.abspath(os.path.join(os.getcwd(), '../../..'))
        os.chdir(project_dir)

        mock_msg = {
          "uuid": str(uuid.uuid4()),
          "publication_name": "AT15-51.dbf",
          "path": "data/files/public/idata_files/AT15-51.dbf",
          "type": "single"
        }
        mock_body = json.dumps(mock_msg, indent=4)
        mock_body = mock_body.encode()
        callback(None, None, None, mock_body)
