import json


class Publication:
    def __init__(self, publication_type=None, title='', creator='', description='', keywords=''):
        self.publication_type = publication_type
        self.title = title
        self.creator = creator
        self.description = description
        self.keywords = keywords
        self.files = {}

    def update_metadata(self, publication_type=None, title=None, creator=None, description=None, keywords=None):
        """
        Updates the metadata for the publication.

        :param publication_type: The type of the publication
        :param title: The title of the publication
        :param creator: The creator of the publication
        :param description: The description of the publication
        :param keywords: The keywords associated with the publication
        """
        if publication_type:
            self.publication_type = publication_type
        if title:
            self.title = title
        if creator:
            self.creator = creator
        if description:
            self.description = description
        if keywords:
            self.keywords = keywords

    def __repr__(self):
        return f"Publication(type={self.publication_type}, title={self.title}, creator={self.creator}, status={self.status})"


class Message:
    def __init__(self, body):
        msg_data = json.loads(body.decode())
        self.uuid = msg_data.get('uuid')
        self.user_jupyter_token = msg_data.get('user_jupyter_token')
        self.path = msg_data.get('path')
        self.publication_name = msg_data.get('publication_name')
        self.type = msg_data.get('type')
        self.description = msg_data.get('description')
        self.keywords = msg_data.get('keywords')

    @property
    def source_dir(self):
        return self.path

    @property
    def target_dir(self):
        return f"/persistent/{self.uuid}"
