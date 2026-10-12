from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi_injector import Injected

from core.exceptions.base import ApplicationError
from core.logger.factory import create_app_logger
from modules.classification.mappers.classification import (
    map_classify_frame_result_to_response,
)
from modules.classification.services.temporal_smoother.service import TemporalSmoother
from modules.classification.use_cases.classify_frame.use_case import (
    ClassifyFrameUseCase,
)

logger = create_app_logger()

tags: list = ["Websocket / Classification"]
router = APIRouter(tags=tags)

RESET_MESSAGE = "reset"


@router.websocket("/classify")
async def classify_stream(
    websocket: WebSocket,
    classify_frame_use_case=Injected(ClassifyFrameUseCase),
) -> None:
    await websocket.accept()
    smoother = TemporalSmoother()

    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break

            if message.get("text") == RESET_MESSAGE:
                smoother.reset()
                await websocket.send_json({"data": None, "error": None})
                continue

            image_bytes = message.get("bytes")
            if not image_bytes:
                await websocket.send_json(
                    {"data": None, "error": {"message": "INVALID_IMAGE"}}
                )
                continue

            try:
                result = await classify_frame_use_case.execute(image_bytes, smoother)
            except ApplicationError as exc:
                await websocket.send_json({"data": None, "error": {"message": str(exc)}})
                continue

            response = map_classify_frame_result_to_response(result)
            await websocket.send_json({"data": response.model_dump(), "error": None})
    except WebSocketDisconnect:
        pass
    finally:
        logger.info("Classification websocket closed")
