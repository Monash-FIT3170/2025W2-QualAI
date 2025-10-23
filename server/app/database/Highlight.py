import sqlite3
import json
from app.config import config


class Highlight:
    """
    A class that allows interaction with transcription highlights in the database.
    """

    def __init__(self, database_name: str) -> None:
        self.db_name = database_name
        self._create_table()

    def _create_table(self) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {config.DB_HIGHLIGHT_TABLE_NAME} (
                    highlight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transcription_id INTEGER NOT NULL,
                    highlighter_id INTEGER,
                    start_offset INTEGER NOT NULL,
                    end_offset INTEGER NOT NULL,
                    color TEXT NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transcription_id)
                        REFERENCES {config.DB_TRANS_TABLE_NAME}(transcription_id)
                        ON DELETE CASCADE
                )
            """
            )

    def insert(self, transcription_id: int, start: int, end: int, color: str, comment: str = None, highlighter_id: int = None) -> int:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                INSERT INTO {config.DB_HIGHLIGHT_TABLE_NAME}
                    (transcription_id, highlighter_id, start_offset, end_offset, color, comment)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (transcription_id, highlighter_id, start, end, color, comment),
            )
            return cur.lastrowid

    def get_all_for_transcription(self, transcription_id: int) -> list[dict]:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT highlight_id, start_offset, end_offset, color, comment
                FROM {config.DB_HIGHLIGHT_TABLE_NAME}
                WHERE transcription_id = ?
                ORDER BY start_offset
            """,
                (transcription_id,),
            )
            rows = cur.fetchall()
            return [
                {
                    "highlight_id": r[0],
                    "startOffset": r[1],
                    "endOffset": r[2],
                    "color": r[3],
                    "comment": r[4],
                }
                for r in rows
            ]

    def delete(self, highlight_id: int) -> bool:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                f"DELETE FROM {config.DB_HIGHLIGHT_TABLE_NAME} WHERE highlight_id = ?",
                (highlight_id,),
            )
            conn.commit()
            deleted = cur.rowcount > 0  # True if something was deleted
        return deleted

    def delete_all_for_transcription(self, transcription_id: int) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                f"DELETE FROM {config.DB_HIGHLIGHT_TABLE_NAME} WHERE transcription_id = ?",
                (transcription_id,),
            )
