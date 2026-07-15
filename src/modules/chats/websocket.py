from fastapi import APIRouter, WebSocket

router = APIRouter(prefix="/chats", tags=["Websocket / Chats"])


@router.websocket("/{room_id}")
async def chat_room(websocket: WebSocket, room_id: str): ...
