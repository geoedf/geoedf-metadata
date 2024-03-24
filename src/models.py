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
