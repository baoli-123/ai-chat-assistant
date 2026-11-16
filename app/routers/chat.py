from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import os
import httpx
from typing import List

from app.database import get_db
from app.models import Message, User, KnowledgeDoc

router = APIRouter()
SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
OPENAI_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

class ChatReq(BaseModel):
    message: str

def get_user_from_token(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        uid = int(payload.get("sub"))
        user = db.query(User).get(uid)
        if not user:
            raise HTTPException(401, "User not found")
        return user
    except JWTError:
        raise HTTPException(401, "Invalid token")

async def call_llm(messages: List[dict]) -> str:
    if not OPENAI_KEY:
        return "[Demo mode] Configure OPENAI_API_KEY to get real AI responses."
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{OPENAI_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}"},
            json={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.7},
        )
        data = resp.json()
        return data["choices"][0]["message"]["content"]

@router.post("/send")
async def send(req: ChatReq, token: str = "", db: Session = Depends(get_db)):
    user = get_user_from_token(token, db)
    db.add(Message(user_id=user.id, role="user", content=req.message))
    db.commit()

    history = db.query(Message).filter(Message.user_id == user.id)\
        .order_by(Message.id.desc()).limit(10).all()
    history = list(reversed(history))
    msgs = [{"role": m.role, "content": m.content} for m in history]

    reply = await call_llm(msgs)
    db.add(Message(user_id=user.id, role="assistant", content=reply))
    db.commit()
    return {"reply": reply}

@router.websocket("/ws/{token}")
async def ws_chat(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            await websocket.send_json({"type": "thinking"})
            reply = await call_llm([{"role": "user", "content": text}])
            await websocket.send_json({"type": "reply", "content": reply})
    except WebSocketDisconnect:
        pass

@router.post("/kb/upload")
async def upload_kb(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8", errors="ignore")
    doc = KnowledgeDoc(filename=file.filename, content=content[:50000])
    db.add(doc)
    db.commit()
    return {"filename": file.filename, "chunks": len(content) // 500}
