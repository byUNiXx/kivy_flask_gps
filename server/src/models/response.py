class ResponseJSON:

    def __init__(self, success, data, error):
        self.success = success
        self.data = data
        self.error = error

    def serialize(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "meta": {
                "copyright": "Copyright (C) 2007 Free Software Foundation, Inc.",
                "authors": "Juan Luis Casañ"
            }
        }
