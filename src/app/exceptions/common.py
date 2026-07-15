from typing import Dict


class ValidationError(Exception):
    def __init__(self, validation_errors: Dict[str, str]) -> None:
        self.validation_errors = validation_errors
        super().__init__("VALIDATION_ERROR")


class ResourceNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("RESOURCE_NOT_FOUND")


class MethodNotAllowedError(Exception):
    def __init__(self) -> None:
        super().__init__("METHOD_NOT_ALLOWED")


class UnsupportedMediaTypeError(Exception):
    def __init__(self) -> None:
        super().__init__("MEDIA_TYPE_NOT_SUPPORTED")


class RequestBodyRequiredError(Exception):
    def __init__(self) -> None:
        super().__init__("REQUEST_BODY_REQUIRED")


class InvalidJSONFormatError(Exception):
    def __init__(self) -> None:
        super().__init__("INVALID_JSON_FORMAT")


class InternalServerError(Exception):
    def __init__(self) -> None:
        super().__init__("INTERNAL_SERVER_ERROR")
