from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from passlib.context import CryptContext

from . import storage

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="People Match API")


class AuthRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class QuestionAnswerRequest(BaseModel):
    username: str
    question_id: int
    answer: bool


class QuestionSkipRequest(BaseModel):
    username: str
    question_id: int


class AskQuestionRequest(BaseModel):
    username: str
    question_text: str = Field(..., min_length=1, max_length=200)
    desired_answer: bool


class AskExistingQuestionRequest(BaseModel):
    username: str
    question_id: int
    desired_answer: bool


class MatchResponse(BaseModel):
    match: str | None
    score: float | None


storage.init_db()


def get_db():
    conn = storage.get_connection()
    try:
        yield conn
    finally:
        conn.close()


def _get_user_id_or_404(conn, username: str) -> int:
    user_id = storage.get_user_id(conn, username)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_id


@app.post("/api/register")
def register(payload: AuthRequest, conn=Depends(get_db)):
    existing = storage.get_user_by_username(conn, payload.username)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    password_hash = pwd_context.hash(payload.password)
    user_id = storage.create_user(conn, payload.username, password_hash)
    return {"id": user_id, "username": payload.username}


@app.post("/api/login")
def login(payload: AuthRequest, conn=Depends(get_db)):
    user = storage.get_user_by_username(conn, payload.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not pwd_context.verify(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": payload.username}


@app.get("/api/questions/next")
def next_question(username: str, conn=Depends(get_db)):
    user_id = _get_user_id_or_404(conn, username)
    question = storage.get_next_question(conn, user_id)
    if not question:
        return {"question": None}
    return {"question": {"id": question.id, "text": question.text}}


@app.post("/api/questions/answer")
def answer_question(payload: QuestionAnswerRequest, conn=Depends(get_db)):
    user_id = _get_user_id_or_404(conn, payload.username)
    storage.record_answer(conn, user_id, payload.question_id, payload.answer)
    question = storage.get_next_question(conn, user_id)
    return {
        "question": {"id": question.id, "text": question.text} if question else None,
    }


@app.post("/api/questions/skip")
def skip_question(payload: QuestionSkipRequest, conn=Depends(get_db)):
    user_id = _get_user_id_or_404(conn, payload.username)
    storage.skip_question(conn, user_id, payload.question_id)
    question = storage.get_next_question(conn, user_id)
    return {
        "question": {"id": question.id, "text": question.text} if question else None,
    }


@app.post("/api/questions/ask")
def ask_question(payload: AskQuestionRequest, conn=Depends(get_db)):
    user_id = _get_user_id_or_404(conn, payload.username)
    question_id = storage.ensure_question(conn, payload.question_text.strip())
    storage.add_asked_question(conn, user_id, question_id, payload.desired_answer)
    return {"question_id": question_id}


@app.post("/api/questions/ask-existing")
def ask_existing_question(payload: AskExistingQuestionRequest, conn=Depends(get_db)):
    user_id = _get_user_id_or_404(conn, payload.username)
    storage.add_asked_question(conn, user_id, payload.question_id, payload.desired_answer)
    return {"question_id": payload.question_id}


@app.get("/api/match/check", response_model=MatchResponse)
def check_match(username: str, conn=Depends(get_db)):
    user_id = _get_user_id_or_404(conn, username)
    match = storage.get_mutual_match(conn, user_id)
    if not match:
        return MatchResponse(match=None, score=None)
    return MatchResponse(match=match[0], score=match[1])
