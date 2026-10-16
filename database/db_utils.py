import os
from contextlib import contextmanager

import bcrypt
import psycopg
from psycopg.rows import dict_row


DEFAULT_DATABASE_URL = "postgresql://drake@127.0.0.1:5543/drake_ai"


def get_database_url():
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_connection():
    return psycopg.connect(get_database_url(), row_factory=dict_row)


@contextmanager
def _connection():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_extended_schema():
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGSERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_ci ON users (LOWER(username))")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS universal_docs (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    filename TEXT NOT NULL,
                    doc_category TEXT NOT NULL DEFAULT 'GENERAL',
                    markdown TEXT NOT NULL,
                    confidence_score DOUBLE PRECISION NOT NULL DEFAULT 0,
                    extraction_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    app_type TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_user_date ON universal_docs(user_id, extraction_date DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_user_app_session ON chat_history(user_id, app_type, session_id, id)")

            cursor.execute("SELECT 1 FROM users WHERE id = 1")
            if cursor.fetchone() is None:
                guest_hash = bcrypt.hashpw(b"local-guest-account", bcrypt.gensalt()).decode("utf-8")
                cursor.execute(
                    "INSERT INTO users(id, username, password_hash) VALUES (1, 'Guest', %s)",
                    (guest_hash,),
                )
            cursor.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), GREATEST((SELECT MAX(id) FROM users), 1))")


def register_user(username, password):
    username = (username or "").strip()
    if not username or not password:
        return False, "Username and password are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if len(password.encode("utf-8")) > 72:
        return False, "Password must be at most 72 UTF-8 bytes."
    initialize_extended_schema()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        with _connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO users(username, password_hash) VALUES (%s, %s)", (username, password_hash))
        return True, "Account created. You can now log in."
    except psycopg.errors.UniqueViolation:
        return False, "That username is already registered."


def verify_login(username, password):
    if len((password or "").encode("utf-8")) > 72:
        return False, None
    initialize_extended_schema()
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, password_hash FROM users WHERE LOWER(username) = LOWER(%s)",
                ((username or "").strip(),),
            )
            row = cursor.fetchone()
    if row and bcrypt.checkpw((password or "").encode("utf-8"), row["password_hash"].encode("utf-8")):
        return True, row["id"]
    return False, None


def archive_document(user_id, filename, category, markdown, confidence):
    initialize_extended_schema()
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO universal_docs (user_id, filename, doc_category, markdown, confidence_score)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (int(user_id), filename, category or "GENERAL", markdown, float(confidence)))
            return cursor.fetchone()["id"]


def get_user_vault(user_id):
    initialize_extended_schema()
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, filename, doc_category, confidence_score, extraction_date
                FROM universal_docs WHERE user_id = %s
                ORDER BY extraction_date DESC, id DESC
            """, (int(user_id),))
            rows = cursor.fetchall()
    return [(r["id"], r["filename"], r["doc_category"], r["confidence_score"], r["extraction_date"].isoformat()) for r in rows]


def get_document_markdown(document_id, user_id):
    initialize_extended_schema()
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT markdown FROM universal_docs WHERE id = %s AND user_id = %s", (int(document_id), int(user_id)))
            row = cursor.fetchone()
    return row["markdown"] if row else None


def delete_document(document_id, user_id):
    initialize_extended_schema()
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM universal_docs WHERE id = %s AND user_id = %s", (int(document_id), int(user_id)))
            return cursor.rowcount > 0


def save_chat_message(user_id, app_type, session_id, role, content):
    initialize_extended_schema()
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO chat_history(user_id, app_type, session_id, role, content)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (int(user_id), app_type, str(session_id), role, content))
            return cursor.fetchone()["id"]


def get_chat_history(user_id, app_type, session_id=None):
    initialize_extended_schema()
    sql = "SELECT role, content, session_id, created_at FROM chat_history WHERE user_id = %s AND app_type = %s"
    params = [int(user_id), app_type]
    if session_id is not None:
        sql += " AND session_id = %s"
        params.append(str(session_id))
    sql += " ORDER BY id ASC"
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]


def delete_chat_history(user_id, app_type, session_id=None):
    initialize_extended_schema()
    sql = "DELETE FROM chat_history WHERE user_id = %s AND app_type = %s"
    params = [int(user_id), app_type]
    if session_id is not None:
        sql += " AND session_id = %s"
        params.append(str(session_id))
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount
