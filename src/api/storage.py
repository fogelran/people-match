from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "people_match.db"

SEED_QUESTIONS: list[str] = [
    "Do you want kids in the future?",
    "Are you looking for a long-term relationship?",
    "Do you enjoy outdoor activities?",
    "Are you a morning person?",
    "Do you like pets?",
    "Do you prefer city living over rural areas?",
    "Is travel important to you?",
    "Do you like to cook at home?",
    "Are you open to relocation?",
    "Do you enjoy live music events?",
    "Do you prefer a quiet night in over a night out?",
    "Is fitness part of your routine?",
    "Do you like trying new restaurants?",
    "Do you enjoy hiking?",
    "Are you an introvert?",
    "Do you enjoy group activities?",
    "Do you value spontaneity?",
    "Is financial planning important to you?",
    "Do you enjoy reading books?",
    "Are you a fan of board games?",
    "Do you like watching movies at home?",
    "Do you enjoy art museums?",
    "Are you interested in volunteering?",
    "Do you like visiting farmers markets?",
    "Do you enjoy beach vacations?",
    "Are you comfortable with pets at home?",
    "Do you want to own a home someday?",
    "Do you enjoy weekend getaways?",
    "Do you prefer texting over phone calls?",
    "Do you like coffee more than tea?",
    "Do you enjoy morning workouts?",
    "Is work-life balance a priority?",
    "Do you like trying new hobbies?",
    "Do you enjoy comedy shows?",
    "Do you like hosting friends at home?",
    "Do you enjoy road trips?",
    "Do you enjoy dancing?",
    "Is environmental sustainability important to you?",
    "Do you like planning trips in advance?",
    "Are you okay with long-distance relationships?",
    "Do you like gardening?",
    "Do you enjoy gaming?",
    "Do you like petsitting for friends?",
    "Are you interested in entrepreneurship?",
    "Do you enjoy yoga or meditation?",
    "Do you prefer early dinners?",
    "Do you enjoy attending sports events?",
    "Do you like minimalist living?",
    "Are you okay with shared finances?",
    "Do you enjoy surprise gifts?",
]


@dataclass(frozen=True)
class Question:
    id: int
    text: str


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                answer INTEGER,
                skipped INTEGER DEFAULT 0,
                UNIQUE(user_id, question_id)
            );
            CREATE TABLE IF NOT EXISTS asked_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                desired_answer INTEGER NOT NULL,
                UNIQUE(user_id, question_id)
            );
            """
        )
    seed_questions(conn, SEED_QUESTIONS)


def seed_questions(conn: sqlite3.Connection, questions: Iterable[str]) -> None:
    with conn:
        for question in questions:
            conn.execute("INSERT OR IGNORE INTO questions (text) VALUES (?)", (question,))


def create_user(conn: sqlite3.Connection, username: str, password_hash: str) -> int:
    with conn:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
    return int(cursor.lastrowid)


def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[sqlite3.Row]:
    cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()


def get_user_id(conn: sqlite3.Connection, username: str) -> Optional[int]:
    row = get_user_by_username(conn, username)
    if row is None:
        return None
    return int(row["id"])


def get_next_question(conn: sqlite3.Connection, user_id: int) -> Optional[Question]:
    cursor = conn.execute(
        """
        SELECT q.id, q.text
        FROM questions q
        LEFT JOIN answers a
          ON q.id = a.question_id AND a.user_id = ?
        WHERE a.id IS NULL
        ORDER BY q.id
        LIMIT 1
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    if row:
        return Question(id=int(row["id"]), text=row["text"])

    cursor = conn.execute(
        """
        SELECT q.id, q.text
        FROM questions q
        JOIN answers a
          ON q.id = a.question_id
        WHERE a.user_id = ? AND a.skipped = 1
        ORDER BY q.id
        LIMIT 1
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    if row:
        return Question(id=int(row["id"]), text=row["text"])
    return None


def record_answer(conn: sqlite3.Connection, user_id: int, question_id: int, answer: bool) -> None:
    with conn:
        conn.execute(
            """
            INSERT INTO answers (user_id, question_id, answer, skipped)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(user_id, question_id) DO UPDATE SET
              answer = excluded.answer,
              skipped = 0
            """,
            (user_id, question_id, int(bool(answer))),
        )


def skip_question(conn: sqlite3.Connection, user_id: int, question_id: int) -> None:
    with conn:
        conn.execute(
            """
            INSERT INTO answers (user_id, question_id, answer, skipped)
            VALUES (?, ?, NULL, 1)
            ON CONFLICT(user_id, question_id) DO UPDATE SET
              answer = NULL,
              skipped = 1
            """,
            (user_id, question_id),
        )


def ensure_question(conn: sqlite3.Connection, question_text: str) -> int:
    with conn:
        conn.execute("INSERT OR IGNORE INTO questions (text) VALUES (?)", (question_text,))
    cursor = conn.execute("SELECT id FROM questions WHERE text = ?", (question_text,))
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("Failed to load question")
    return int(row["id"])


def add_asked_question(
    conn: sqlite3.Connection,
    user_id: int,
    question_id: int,
    desired_answer: bool,
) -> None:
    with conn:
        conn.execute(
            """
            INSERT INTO asked_questions (user_id, question_id, desired_answer)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, question_id) DO UPDATE SET
              desired_answer = excluded.desired_answer
            """,
            (user_id, question_id, int(bool(desired_answer))),
        )


def get_mutual_match(conn: sqlite3.Connection, user_id: int) -> Optional[tuple[str, float]]:
    candidates = conn.execute("SELECT id, username FROM users WHERE id != ?", (user_id,)).fetchall()
    best_match: Optional[tuple[str, float]] = None

    seeker_questions = conn.execute(
        "SELECT question_id, desired_answer FROM asked_questions WHERE user_id = ?",
        (user_id,),
    ).fetchall()

    for candidate in candidates:
        candidate_id = int(candidate["id"])
        candidate_name = candidate["username"]

        if not _matches_preferences(conn, candidate_id, seeker_questions):
            continue

        candidate_questions = conn.execute(
            "SELECT question_id, desired_answer FROM asked_questions WHERE user_id = ?",
            (candidate_id,),
        ).fetchall()

        if not _matches_preferences(conn, user_id, candidate_questions):
            continue

        total_preferences = len(seeker_questions) + len(candidate_questions)
        if total_preferences == 0:
            continue
        score = total_preferences
        ratio = score / total_preferences
        if best_match is None or ratio > best_match[1]:
            best_match = (candidate_name, ratio)

    return best_match


def _matches_preferences(
    conn: sqlite3.Connection,
    user_id: int,
    preferences: Iterable[sqlite3.Row],
) -> bool:
    for preference in preferences:
        question_id = int(preference["question_id"])
        desired_answer = int(preference["desired_answer"])
        answer_row = conn.execute(
            """
            SELECT answer
            FROM answers
            WHERE user_id = ? AND question_id = ? AND skipped = 0
            """,
            (user_id, question_id),
        ).fetchone()
        if answer_row is None:
            return False
        if answer_row["answer"] is None:
            return False
        if int(answer_row["answer"]) != desired_answer:
            return False
    return True
