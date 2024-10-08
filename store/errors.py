class StoreException(Exception):
    def __init__(self, status: int, details: str, error: str) -> None:
        super().__init__(f"Status {status} | Details: {details} | Error: {error}")
        self.status = status
        self.error = error
        self.details = details


class ClosedStore(StoreException):
    pass


class NotFound(StoreException):
    pass


class ValidationError(StoreException):
    pass


class ServerError(StoreException):
    pass


class UnsupportedRequest(StoreException):
    pass
