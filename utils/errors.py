"""
Errors the pipeline raises on purpose - Sheria Yangu

Each one has a clear cause that a caller can explain to the user, so the API
and the demo can answer with a plain message instead of a server error.
"""


class UnreadableDocumentError(Exception):
    """The upload or the pasted text holds no text the pipeline can read."""


class ModelOutputError(Exception):
    """A model reply was empty, was not JSON, or did not have the expected shape."""
