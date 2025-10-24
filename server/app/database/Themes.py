import sqlite3
import json
from app.config import config


class Theme:
    """
    A class that manages themes in the database. Themes are collections of codes.
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
                CREATE TABLE IF NOT EXISTS {config.DB_THEME_TABLE_NAME} (
                    theme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    theme_name TEXT NOT NULL,
                    codes TEXT NOT NULL,  -- Stores JSON array of code IDs
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) 
                        REFERENCES {config.DB_PROJECT_TABLE_NAME}(project_id)
                        ON DELETE CASCADE
                )
            """
            )

    def clear_themes_by_project(self, project_id: int) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM themes WHERE project_id = ?",
                (project_id,),
            )

    def insert(self, project_id: int, theme_name: str, codes: list) -> int:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO themes (project_id, theme_name, codes) VALUES (?, ?, ?)",
                (project_id, theme_name, json.dumps(codes)),
            )
            return cur.lastrowid

    def get_themes_by_project(self, project_id: int) -> list:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT theme_id, theme_name, codes
                FROM {config.DB_THEME_TABLE_NAME}
                WHERE project_id = ?
                """,
                (project_id,),
            )
            return cur.fetchall()

    def delete(self, theme_id: int) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM themes WHERE theme_id = ?", (theme_id,))
            if cur.rowcount == 0:
                raise ValueError(f"Theme with ID {theme_id} not found")
