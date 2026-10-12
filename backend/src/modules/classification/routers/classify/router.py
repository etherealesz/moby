from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi_injector import Injected

from app.schemas.predefined import SGenericErrorResponse, SStandardValidationErrorResponse
from app.schemas.response import SStandardResponse
from app.utils.standard_response_builder import StandardResponseBuilder
from modules.classification.exceptions.classification import (
    ClassifierLabelMismatchError,
    ClassifierModelNotAvailableError,
    DetectorModelNotAvailableError,
    InvalidImageError,
)
from modules.classification.mappers.classification import (
    map_classify_frame_result_to_response,
)
from modules.classification.schemas.classification import SClassifyFrameResponse
from modules.classification.use_cases.classify_frame.use_case import (
    ClassifyFrameUseCase,
)

tags: list = ["API / Classification"]
router = APIRouter(prefix="/classify", tags=tags)


@router.post(
    path="",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SGenericErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": SStandardValidationErrorResponse
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": SGenericErrorResponse},
    },
)
async def classify_frame(
    file: UploadFile = File(description="Satu frame kamera (JPEG/PNG)"),
    classify_frame_use_case=Injected(ClassifyFrameUseCase),
) -> SStandardResponse[SClassifyFrameResponse]:
    image_bytes = await file.read()

    try:
        result = await classify_frame_use_case.execute(image_bytes)
    except InvalidImageError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except (
        DetectorModelNotAvailableError,
        ClassifierModelNotAvailableError,
        ClassifierLabelMismatchError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    response_data = map_classify_frame_result_to_response(result)
    return (
        StandardResponseBuilder()
        .set_status_code(status.HTTP_200_OK)
        .set_data(response_data)
        .build()
    )
