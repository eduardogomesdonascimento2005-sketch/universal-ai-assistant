from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from core.agent import ProfessionalAgent
from database import SessionLocal, User, ChatMessage

app = FastAPI(title="IA Profissional Real", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
agent = ProfessionalAgent()


class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    username: str
    prompt: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok", "service": "IA Profissional Real"}


@app.post("/register")
async def register(data: LoginRequest):
    db = SessionLocal()
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Usuário já existe")

    new_user = User(username=data.username, password=data.password)
    db.add(new_user)
    db.commit()
    db.close()
    return {"status": "ok", "username": data.username}


@app.post("/login")
async def login(data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.username == data.username).first()
    db.close()

    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    return {"status": "ok", "username": user.username}


@app.post("/chat")
async def chat(data: ChatRequest):
    if not data.username or not data.prompt.strip():
        raise HTTPException(status_code=400, detail="Usuário e prompt são obrigatórios")

    response = agent.respond(data.username, data.prompt)

    db = SessionLocal()
    db.add(ChatMessage(username=data.username, prompt=data.prompt, response=response))
    db.commit()
    db.close()

    return {"response": response}
