from modules.classification.schemas.classification import (
    SBoundingBoxResponse,
    SClassifiedObjectResponse,
    SClassifyFrameResponse,
)
from modules.classification.use_cases.classify_frame.dto import (
    DClassifiedObject,
    DClassifyFrameResult,
)


def map_classified_object_to_response(
    item: DClassifiedObject,
) -> SClassifiedObjectResponse:
    return SClassifiedObjectResponse(
        track_id=item.track_id,
        box=SBoundingBoxResponse(
            x1=round(item.x1, 1),
            y1=round(item.y1, 1),
            x2=round(item.x2, 1),
            y2=round(item.y2, 1),
        ),
        label=item.label,
        confidence=round(item.confidence, 4),
        detection_confidence=round(item.detection_confidence, 4),
        probabilities={label: round(p, 4) for label, p in item.probabilities.items()},
    )


def map_classify_frame_result_to_response(
    result: DClassifyFrameResult,
) -> SClassifyFrameResponse:
    return SClassifyFrameResponse(
        width=result.width,
        height=result.height,
        objects=[map_classified_object_to_response(item) for item in result.objects],
        preprocess_time_ms=round(result.preprocess_time_ms, 3),
        detection_time_ms=round(result.detection_time_ms, 3),
        classification_time_ms=round(result.classification_time_ms, 3),
        total_time_ms=round(result.total_time_ms, 3),
    )
