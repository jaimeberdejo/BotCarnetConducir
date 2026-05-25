from __future__ import annotations

import json
import random
import sqlite3
from pathlib import Path

from .models import Question, QuestionDraft


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_id TEXT,
            prompt TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            correct_index INTEGER NOT NULL,
            explanation TEXT NOT NULL DEFAULT '',
            image_name TEXT,
            telegram_file_id TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'approved',
            submitted_by INTEGER,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_type, source_id)
        );

        CREATE TABLE IF NOT EXISTS answer_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            mode TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            answered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(question_id) REFERENCES questions(id)
        );

        CREATE TABLE IF NOT EXISTS exam_sessions (
            user_id INTEGER PRIMARY KEY,
            question_ids TEXT NOT NULL,
            current_index INTEGER NOT NULL,
            mistakes INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            review_data TEXT NOT NULL DEFAULT '[]',
            started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_state (
            user_id INTEGER PRIMARY KEY,
            practice_question_id INTEGER,
            last_bank_question_id INTEGER,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(practice_question_id) REFERENCES questions(id),
            FOREIGN KEY(last_bank_question_id) REFERENCES questions(id)
        );

        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            mistakes INTEGER NOT NULL,
            passed INTEGER NOT NULL,
            finished_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(exam_sessions)").fetchall()
    }
    if "review_data" not in columns:
        conn.execute(
            "ALTER TABLE exam_sessions ADD COLUMN review_data TEXT NOT NULL DEFAULT '[]'"
        )
    question_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(questions)").fetchall()
    }
    if "telegram_file_id" not in question_columns:
        conn.execute("ALTER TABLE questions ADD COLUMN telegram_file_id TEXT")
    conn.commit()


def set_metadata(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO metadata (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
        """,
        (key, value),
    )
    conn.commit()


def get_metadata(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
    if row is None:
        return None
    return str(row["value"])


def count_imported_questions(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM questions WHERE source_type = 'imported'"
    ).fetchone()
    return int(row["total"])


def upsert_question(conn: sqlite3.Connection, draft: QuestionDraft) -> None:
    conn.execute(
        """
        INSERT INTO questions (
            source_type, source_id, prompt, option_a, option_b, option_c,
            correct_index, explanation, image_name, status, submitted_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_type, source_id) DO UPDATE SET
            prompt = excluded.prompt,
            option_a = excluded.option_a,
            option_b = excluded.option_b,
            option_c = excluded.option_c,
            correct_index = excluded.correct_index,
            explanation = excluded.explanation,
            image_name = excluded.image_name,
            status = excluded.status
        """,
        (
            draft.source_type,
            draft.source_id,
            draft.prompt,
            draft.option_a,
            draft.option_b,
            draft.option_c,
            draft.correct_index,
            draft.explanation,
            draft.image_name,
            draft.status,
            draft.submitted_by,
        ),
    )


def add_user_submission(conn: sqlite3.Connection, draft: QuestionDraft) -> None:
    conn.execute(
        """
        INSERT INTO questions (
            source_type, source_id, prompt, option_a, option_b, option_c,
            correct_index, explanation, image_name, status, submitted_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            draft.source_type,
            draft.source_id,
            draft.prompt,
            draft.option_a,
            draft.option_b,
            draft.option_c,
            draft.correct_index,
            draft.explanation,
            draft.image_name,
            draft.status,
            draft.submitted_by,
        ),
    )
    conn.commit()


def row_to_question(row: sqlite3.Row) -> Question:
    return Question(
        id=int(row["id"]),
        prompt=row["prompt"],
        option_a=row["option_a"],
        option_b=row["option_b"],
        option_c=row["option_c"],
        correct_index=int(row["correct_index"]),
        explanation=row["explanation"] or "",
        image_name=row["image_name"],
        telegram_file_id=row["telegram_file_id"],
        source_type=row["source_type"],
        status=row["status"],
    )


def get_question_by_id(conn: sqlite3.Connection, question_id: int) -> Question | None:
    row = conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
    return row_to_question(row) if row else None


def get_random_imported_question(conn: sqlite3.Connection) -> Question | None:
    row = conn.execute(
        """
        SELECT * FROM questions
        WHERE source_type = 'imported' AND is_active = 1
        ORDER BY RANDOM()
        LIMIT 1
        """
    ).fetchone()
    return row_to_question(row) if row else None


def count_active_imported_questions(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM questions
        WHERE source_type = 'imported' AND is_active = 1
        """
    ).fetchone()
    return int(row["total"])


def list_imported_questions(
    conn: sqlite3.Connection, offset: int, limit: int
) -> list[Question]:
    rows = conn.execute(
        """
        SELECT *
        FROM questions
        WHERE source_type = 'imported' AND is_active = 1
        ORDER BY id
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()
    return [row_to_question(row) for row in rows]


def set_practice_question(conn: sqlite3.Connection, user_id: int, question_id: int) -> None:
    conn.execute(
        """
        INSERT INTO user_state (user_id, practice_question_id, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            practice_question_id = excluded.practice_question_id,
            updated_at = CURRENT_TIMESTAMP
        """,
        (user_id, question_id),
    )
    conn.commit()


def set_question_telegram_file_id(
    conn: sqlite3.Connection, question_id: int, telegram_file_id: str
) -> None:
    conn.execute(
        "UPDATE questions SET telegram_file_id = ? WHERE id = ?",
        (telegram_file_id, question_id),
    )
    conn.commit()


def set_bank_question(conn: sqlite3.Connection, user_id: int, question_id: int) -> None:
    conn.execute(
        """
        INSERT INTO user_state (user_id, last_bank_question_id, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            last_bank_question_id = excluded.last_bank_question_id,
            updated_at = CURRENT_TIMESTAMP
        """,
        (user_id, question_id),
    )
    conn.commit()


def log_answer(
    conn: sqlite3.Connection, user_id: int, question_id: int, mode: str, is_correct: bool
) -> None:
    conn.execute(
        """
        INSERT INTO answer_events (user_id, question_id, mode, is_correct)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, question_id, mode, int(is_correct)),
    )
    conn.commit()


def create_exam_session(
    conn: sqlite3.Connection, user_id: int, question_ids: list[int]
) -> None:
    conn.execute(
        """
        INSERT INTO exam_sessions (
            user_id, question_ids, current_index, mistakes, correct_count, review_data
        )
        VALUES (?, ?, 0, 0, 0, '[]')
        ON CONFLICT(user_id) DO UPDATE SET
            question_ids = excluded.question_ids,
            current_index = 0,
            mistakes = 0,
            correct_count = 0,
            review_data = '[]',
            started_at = CURRENT_TIMESTAMP
        """,
        (user_id, json.dumps(question_ids)),
    )
    conn.commit()


def load_exam_session(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM exam_sessions WHERE user_id = ?", (user_id,)
    ).fetchone()


def clear_exam_session(conn: sqlite3.Connection, user_id: int) -> None:
    conn.execute("DELETE FROM exam_sessions WHERE user_id = ?", (user_id,))
    conn.commit()


def pick_exam_question_ids(conn: sqlite3.Connection, count: int) -> list[int]:
    rows = conn.execute(
        """
        SELECT id FROM questions
        WHERE source_type = 'imported' AND is_active = 1
        """
    ).fetchall()
    ids = [int(row["id"]) for row in rows]
    if not ids:
        return []
    if len(ids) <= count:
        random.shuffle(ids)
        return ids
    return random.sample(ids, count)


def answer_exam_question(
    conn: sqlite3.Connection, user_id: int, selected_index: int
) -> dict[str, int | bool | Question | None]:
    session = load_exam_session(conn, user_id)
    if not session:
        return {"exists": False}
    question_ids = json.loads(session["question_ids"])
    current_index = int(session["current_index"])
    if current_index >= len(question_ids):
        return {"exists": False}
    question = get_question_by_id(conn, int(question_ids[current_index]))
    if question is None:
        return {"exists": False}
    is_correct = selected_index == question.correct_index
    mistakes = int(session["mistakes"]) + (0 if is_correct else 1)
    correct_count = int(session["correct_count"]) + (1 if is_correct else 0)
    next_index = current_index + 1
    review_data = json.loads(session["review_data"] or "[]")
    review_data.append(
        {
            "question_id": question.id,
            "selected_index": selected_index,
            "correct_index": question.correct_index,
            "is_correct": is_correct,
        }
    )

    conn.execute(
        """
        UPDATE exam_sessions
        SET current_index = ?, mistakes = ?, correct_count = ?, review_data = ?
        WHERE user_id = ?
        """,
        (next_index, mistakes, correct_count, json.dumps(review_data), user_id),
    )
    conn.commit()
    log_answer(conn, user_id, question.id, "exam", is_correct)

    return {
        "exists": True,
        "question": question,
        "is_correct": is_correct,
        "mistakes": mistakes,
        "correct_count": correct_count,
        "current_index": current_index,
        "next_index": next_index,
        "total": len(question_ids),
        "finished": next_index >= len(question_ids),
    }


def get_exam_question(conn: sqlite3.Connection, user_id: int) -> tuple[Question | None, int, int, int]:
    session = load_exam_session(conn, user_id)
    if not session:
        return None, 0, 0, 0
    question_ids = json.loads(session["question_ids"])
    current_index = int(session["current_index"])
    if current_index >= len(question_ids):
        return None, current_index, len(question_ids), int(session["mistakes"])
    question = get_question_by_id(conn, int(question_ids[current_index]))
    return question, current_index, len(question_ids), int(session["mistakes"])


def get_exam_review(conn: sqlite3.Connection, user_id: int) -> list[dict[str, object]]:
    session = load_exam_session(conn, user_id)
    if not session:
        return []
    review_rows = json.loads(session["review_data"] or "[]")
    enriched: list[dict[str, object]] = []
    for row in review_rows:
        question = get_question_by_id(conn, int(row["question_id"]))
        if question is None:
            continue
        enriched.append(
            {
                "question": question,
                "selected_index": int(row["selected_index"]),
                "correct_index": int(row["correct_index"]),
                "is_correct": bool(row["is_correct"]),
            }
        )
    return enriched


def record_exam_result(
    conn: sqlite3.Connection,
    user_id: int,
    total_questions: int,
    correct_count: int,
    mistakes: int,
    passed: bool,
) -> None:
    conn.execute(
        """
        INSERT INTO exam_results (
            user_id, total_questions, correct_count, mistakes, passed
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, total_questions, correct_count, mistakes, int(passed)),
    )
    conn.commit()


def reset_user_stats(conn: sqlite3.Connection, user_id: int) -> None:
    conn.execute("DELETE FROM answer_events WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM exam_results WHERE user_id = ?", (user_id,))
    conn.commit()


def get_user_stats(conn: sqlite3.Connection, user_id: int) -> dict[str, object]:
    totals = conn.execute(
        """
        SELECT
            SUM(CASE WHEN mode = 'practice' AND is_correct = 1 THEN 1 ELSE 0 END) AS practice_correct,
            SUM(CASE WHEN mode = 'practice' AND is_correct = 0 THEN 1 ELSE 0 END) AS practice_incorrect,
            SUM(CASE WHEN mode = 'exam' AND is_correct = 1 THEN 1 ELSE 0 END) AS exam_correct,
            SUM(CASE WHEN mode = 'exam' AND is_correct = 0 THEN 1 ELSE 0 END) AS exam_incorrect
        FROM answer_events
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    recent_errors = conn.execute(
        """
        SELECT q.prompt, COUNT(*) AS misses
        FROM answer_events e
        JOIN questions q ON q.id = e.question_id
        WHERE e.user_id = ? AND e.is_correct = 0
        GROUP BY e.question_id
        ORDER BY misses DESC, e.id DESC
        LIMIT 5
        """,
        (user_id,),
    ).fetchall()

    exam_results = conn.execute(
        """
        SELECT
            SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) AS exams_passed,
            SUM(CASE WHEN passed = 0 THEN 1 ELSE 0 END) AS exams_failed
        FROM exam_results
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    return {
        "practice_correct": int(totals["practice_correct"] or 0),
        "practice_incorrect": int(totals["practice_incorrect"] or 0),
        "exam_correct": int(totals["exam_correct"] or 0),
        "exam_incorrect": int(totals["exam_incorrect"] or 0),
        "exams_passed": int(exam_results["exams_passed"] or 0),
        "exams_failed": int(exam_results["exams_failed"] or 0),
        "recent_errors": [(row["prompt"], int(row["misses"])) for row in recent_errors],
    }
