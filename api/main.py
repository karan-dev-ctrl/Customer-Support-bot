from fastapi import FastAPI
from pydantic import BaseModel

from bot.pipeline import handle_message

app = FastAPI(title="Support Bot API")


class ChatRequest(BaseModel):
    message: str
    session_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    return handle_message(req.message, req.session_id)