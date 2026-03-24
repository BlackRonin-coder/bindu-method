from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from bindu.kernel import BinduKernel


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_FILE = BASE_DIR / "frontend.html"
kernel = BinduKernel()


class BinduRequest(BaseModel):
    subject: str
    request: str


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    if FRONTEND_FILE.exists():
        return FRONTEND_FILE.read_text(encoding="utf-8")
    return """
    <html>
      <body style="font-family: Arial; padding: 24px;">
        <h1>Bindu Python Core</h1>
        <p>The backend is running.</p>
        <p>frontend.html has not been added yet.</p>
      </body>
    </html>
    """


@app.post("/run-wl")
def run_wl(payload: BinduRequest):
    result = kernel.run_wl(payload.subject, payload.request)
    return JSONResponse(content=result.to_dict())