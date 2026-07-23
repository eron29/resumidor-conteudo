import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "app.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_id INTEGER,
            title TEXT NOT NULL,
            source_type TEXT,
            source_ref TEXT,
            content_md TEXT,
            created_at TEXT,
            FOREIGN KEY (folder_id) REFERENCES folders (id) ON DELETE SET NULL
        )
        """
    )
    if not conn.execute("SELECT 1 FROM folders").fetchone():
        conn.execute("INSERT INTO folders (name) VALUES (?)", ("Geral",))
    conn.commit()
    conn.close()


def list_folders():
    conn = _connect()
    rows = conn.execute("SELECT * FROM folders ORDER BY name").fetchall()
    conn.close()
    return rows


def create_folder(name):
    conn = _connect()
    conn.execute("INSERT INTO folders (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def rename_folder(folder_id, new_name):
    conn = _connect()
    conn.execute("UPDATE folders SET name = ? WHERE id = ?", (new_name, folder_id))
    conn.commit()
    conn.close()


def delete_folder(folder_id):
    conn = _connect()
    conn.execute("DELETE FROM summaries WHERE folder_id = ?", (folder_id,))
    conn.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
    conn.commit()
    conn.close()


def save_summary(folder_id, title, source_type, source_ref, content_md):
    conn = _connect()
    conn.execute(
        """
        INSERT INTO summaries (folder_id, title, source_type, source_ref, content_md, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (folder_id, title, source_type, source_ref, content_md, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def list_summaries(folder_id=None):
    conn = _connect()
    query = """
        SELECT s.*, f.name as folder_name
        FROM summaries s
        LEFT JOIN folders f ON s.folder_id = f.id
    """
    if folder_id:
        query += " WHERE s.folder_id = ? ORDER BY s.created_at DESC"
        rows = conn.execute(query, (folder_id,)).fetchall()
    else:
        query += " ORDER BY s.created_at DESC"
        rows = conn.execute(query).fetchall()
    conn.close()
    return rows


def delete_summary(summary_id):
    conn = _connect()
    conn.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))
    conn.commit()
    conn.close()
