from injector import Binder, Module, singleton

from modules.classification.services.image_preprocessor.service import ImagePreprocessor
from modules.classification.services.object_detector.service import ObjectDetector
from modules.classification.services.waste_classifier.service import WasteClassifier
from modules.classification.use_cases.classify_frame.use_case import (
    ClassifyFrameUseCase,
)


class CClassificationModule(Module):
    def configure(self, binder: Binder) -> None:
        self._register_services(binder)
        self._register_use_cases(binder)

    def _register_services(self, binder: Binder) -> None:
        binder.bind(ImagePreprocessor, to=ImagePreprocessor, scope=singleton)
        binder.bind(ObjectDetector, to=ObjectDetector, scope=singleton)
        binder.bind(WasteClassifier, to=WasteClassifier, scope=singleton)

    def _register_use_cases(self, binder: Binder) -> None:
        binder.bind(ClassifyFrameUseCase, to=ClassifyFrameUseCase)
