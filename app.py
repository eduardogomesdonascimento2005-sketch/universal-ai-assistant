from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from universal_ai import UniversalAgent

app = FastAPI(title="IA Universal", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
agent = UniversalAgent()


class PromptRequest(BaseModel):
    prompt: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok", "service": "IA Universal"}


@app.post("/chat")
async def chat(request: PromptRequest):
    if not request.prompt or not request.prompt.strip():
        return {"response": "Digite uma tarefa v��lida."}

    response = agent.run(request.prompt)
    return {"response": response}
