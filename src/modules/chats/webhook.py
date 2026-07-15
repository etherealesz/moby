from fastapi import APIRouter, status

from app.schemas.predefined import SStandardValidationErrorResponse
from app.schemas.response import SStandardListResponse
from app.utils.standard_response_builder import StandardResponseBuilder

router = APIRouter(prefix="/chats", tags=["Webhook / Chats"])


@router.post(
    "/{room_id}",
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": SStandardValidationErrorResponse}
    },
)
async def chat_room(room_id: str) -> SStandardListResponse:
    return StandardResponseBuilder().build()
