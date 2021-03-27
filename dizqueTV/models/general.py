from dizqueTV.models.base import BaseObject


class UploadImageResponse(BaseObject):
    def __init__(self, data: dict):
        super().__init__(data)
        self.name = data.get('name')
        self.mimetype = data.get('mimetype')
        self.size = data.get('size')
        self.fileUrl = data.get('fileUrl')