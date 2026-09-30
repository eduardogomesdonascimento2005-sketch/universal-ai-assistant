import os
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from pathlib import Path

load_dotenv()

app = FastAPI(title="WhatsApp IA Completa")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

DATABASE_URL = "sqlite:///./whatsapp_ai.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, index=True)
    user_message = Column(Text)
    assistant_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


@app.get("/webhook")
async def webhook_verify(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return JSONResponse(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/webhook")
async def webhook_receive(request: Request):
    payload = await request.json()
    if "entry" not in payload:
        return {"status": "ignored"}

    for entry in payload["entry"]:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])

            for msg in messages:
                from_number = msg.get("from")
                text = msg.get("text", {}).get("body", "")
                if not from_number or not text:
                    continue

                response_text = generate_ai_response(from_number, text)

                db = SessionLocal()
                db.add(Conversation(phone=from_number, user_message=text, assistant_message=response_text))
                db.commit()
                db.close()

                send_whatsapp_message(from_number, response_text)

    return {"status": "ok"}


def generate_ai_response(phone: str, user_text: str) -> str:
    db = SessionLocal()
    recent_msgs = db.query(Conversation).filter(Conversation.phone == phone).order_by(Conversation.created_at.desc()).limit(5).all()
    db.close()

    messages = [{"role": "system", "content": "Você é uma IA assistente inteligente, útil, direta e profissional. Responda em português, de forma prática e concisa."}]

    for msg in reversed(recent_msgs):
        messages.append({"role": "user", "content": msg.user_message})
        messages.append({"role": "assistant", "content": msg.assistant_message})

    messages.append({"role": "user", "content": user_text})

    try:
        completion = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Desculpe, houve um erro ao processar sua mensagem: {str(e)}"


def send_whatsapp_message(to_number: str, text: str):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@app.get("/")
async def root():
    return {"status": "ok", "service": "WhatsApp IA Completa"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
