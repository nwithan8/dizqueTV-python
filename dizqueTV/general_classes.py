class UploadImageResponse:
    def __init__(self, data: dict):
        self._data = data
        self.name = data.get('name')
        self.mimetype = data.get('mimetype')
        self.size = data.get('size')
        self.fileUrl = data.get('fileUrl')