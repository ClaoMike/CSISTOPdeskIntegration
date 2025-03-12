from enum import Enum

class RequestType(Enum):
    """
        Enum representing the types of HTTP requests supported by the TOPdesk API.

        Attributes:
            POST: Represents an HTTP POST request (used for creating resources).
            PATCH: Represents an HTTP PATCH request (used for updating resources partially).
            PUT: Represents an HTTP PUT request (used for updating or replacing resources).
    """
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    GET = "GET"
