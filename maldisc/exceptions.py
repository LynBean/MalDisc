
class RequestsException(Exception):
    """Base exception for Requests."""
    pass

class TooManyRequests(RequestsException):
    pass

class RequestsError(RequestsException):
    pass