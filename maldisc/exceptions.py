
class JikanRequestsException(Exception):
    """Base exception for Jikan Requests."""
    pass

class JikanRequestsBadRequests(JikanRequestsException):
    pass
class JikanRequestsNotFound(JikanRequestsException):
    pass
class JikanRequestsTooManyRequests(JikanRequestsException):
    pass
class JikanRequestsInternalServerError(JikanRequestsException):
    pass
class JikanRequestsServiceUnavailable(JikanRequestsException):
    pass
