"""Sakhi API. Stateless: the browser keeps the (tiny) profile, nothing is stored or logged server-side."""
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr

import gemini_service
from dialogue import SLOTS, handle_turn
from scheme_data import LAST_VERIFIED, SCHEMES

load_dotenv()
VERSION = "6.0.0"
Slot = Literal["marital_status", "age", "deserted_years", "assets_over_limit"]

app = FastAPI(title="Sakhi - The Invisible Woman", version=VERSION, docs_url=None, redoc_url=None)
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "microphone=(self)"
    return response


# Tiny in-memory limiter so a public demo cannot drain the Gemini quota.
_hits: Dict[str, deque] = defaultdict(deque)


def limited(request: Request, bucket: str, per_minute: int) -> bool:
    now, key = time.time(), f"{bucket}:{request.client.host if request.client else '?'}"
    q = _hits[key]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= per_minute:
        return True
    q.append(now)
    return False


class ProfileIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    marital_status: Optional[StrictStr] = None
    age: Optional[StrictInt] = None
    deserted_years: Optional[StrictInt] = None
    assets_over_limit: Optional[StrictBool] = None
    docs_ready: list[StrictStr] = Field(default_factory=list, max_length=20)


class AnswerIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    slot: Slot
    value: Union[StrictBool, StrictInt, StrictStr]


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lang: Literal["ta", "en"] = "ta"
    profile: ProfileIn = Field(default_factory=ProfileIn)
    message: Optional[str] = Field(default=None, max_length=500)
    answer: Optional[AnswerIn] = None
    ask: Optional[Slot] = None
    start: bool = False
    pending: Optional[Slot] = None


class TtsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=600)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": VERSION, "gemini": gemini_service.configured(), "tts": gemini_service.tts_enabled(),
            "schemes": len(SCHEMES), "data_verified_on": LAST_VERIFIED}


@app.post("/api/chat")
def chat(body: ChatRequest, request: Request):
    if limited(request, "chat", 90):
        raise HTTPException(429, "Too many requests, please wait a moment.")
    answer = body.answer.model_dump() if body.answer else None
    extractor = gemini_service.extract_facts if gemini_service.configured() else None
    return handle_turn(body.lang, body.profile.model_dump(), message=(body.message or "").strip() or None,
                       answer=answer, ask=body.ask, start=body.start, pending=body.pending, extractor=extractor)


@app.post("/api/tts")
def tts(body: TtsRequest, request: Request):
    if not gemini_service.tts_enabled():
        raise HTTPException(503, "Server speech is not enabled.")
    if limited(request, "tts", 40):
        raise HTTPException(429, "Too many requests, please wait a moment.")
    audio = gemini_service.synthesize(body.text.strip())
    if not audio:
        raise HTTPException(503, "Speech could not be generated.")
    return Response(audio, media_type="audio/wav", headers={"Cache-Control": "private, max-age=86400"})


@app.exception_handler(Exception)
async def unexpected(_: Request, exc: Exception):
    return JSONResponse({"detail": "Something went wrong. Please try again."}, status_code=500)


# Serve the built React app from the same origin (one URL, no CORS, mic works on https hosts).
DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
