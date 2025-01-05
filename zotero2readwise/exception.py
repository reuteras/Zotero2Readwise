"""Exceptions for Zotero2Readwise."""
class Zotero2ReadwiseError(Exception):
    """Exception for Zotero2Readwise."""
    def __init__(self, message: str):
        """Init function for error."""
        self.message = message

        super().__init__(self.message)
