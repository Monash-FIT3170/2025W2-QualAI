import sqlite3
import json
from app.config import config

WEIGHT_FALLBACK = 3


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
                    FOREIGN KEY (highlighter_id)
                        REFERENCES {config.DB_HIGHLIGHTER_TABLE_NAME}(highlighter_id)
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

    def get_project_highlights_with_metadata(self, project_id: int) -> list[dict]:
        """
        Returns highlight snippets for a given project enriched with highlighter metadata.

        Args:
            project_id (int): Project identifier.

        Returns:
            list[dict]: Highlight metadata rows containing snippet, weight, and labels.
        """
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT
                    h.highlight_id,
                    h.start_offset,
                    h.end_offset,
                    h.color,
                    h.comment,
                    t.transcription_id,
                    t.name,
                    SUBSTR(
                        t.transcription,
                        h.start_offset + 1,
                        CASE
                            WHEN h.end_offset > h.start_offset THEN h.end_offset - h.start_offset
                            ELSE 0
                        END
                    ) AS snippet,
                    COALESCE(hi.label, ''),
                    COALESCE(hi.weight, ?),
                    COALESCE(hi.colour, h.color)
                FROM {config.DB_HIGHLIGHT_TABLE_NAME} AS h
                INNER JOIN {config.DB_TRANS_TABLE_NAME} AS t
                    ON t.transcription_id = h.transcription_id
                LEFT JOIN {config.DB_HIGHLIGHTER_TABLE_NAME} AS hi
                    ON hi.highlighter_id = h.highlighter_id
                WHERE t.project_id = ?
                ORDER BY
                    CAST(COALESCE(hi.weight, ?) AS INTEGER) DESC,
                    h.created_at ASC
                """,
                (str(WEIGHT_FALLBACK), project_id, str(WEIGHT_FALLBACK)),
            )

            rows = cur.fetchall()

        highlights = []
        for row in rows:
            (
                highlight_id,
                start_offset,
                end_offset,
                color,
                comment,
                transcription_id,
                transcription_name,
                snippet,
                highlighter_label,
                weight_raw,
                highlighter_colour,
            ) = row

            try:
                weight = int(weight_raw)
            except (TypeError, ValueError):
                weight = WEIGHT_FALLBACK

            highlights.append(
                {
                    "highlight_id": highlight_id,
                    "start_offset": start_offset,
                    "end_offset": end_offset,
                    "color": color,
                    "comment": comment or "",
                    "transcription_id": transcription_id,
                    "transcription_name": transcription_name,
                    "snippet": (snippet or "").strip(),
                    "highlighter_label": highlighter_label or "",
                    "weight": weight,
                    "highlighter_colour": highlighter_colour or color,
                }
            )

        return highlights

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
