from core.exceptions.base import ApplicationError


class InvalidImageError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("INVALID_IMAGE")


class DetectorModelNotAvailableError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("DETECTOR_MODEL_NOT_AVAILABLE")


class ClassifierModelNotAvailableError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("CLASSIFIER_MODEL_NOT_AVAILABLE")


class ClassifierLabelMismatchError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("CLASSIFIER_LABEL_MISMATCH")
