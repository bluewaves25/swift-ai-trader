from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/api/support/chat")
async def support_chat(req: ChatRequest):
    return {"response": "Support is not available yet. Please try again later."} 