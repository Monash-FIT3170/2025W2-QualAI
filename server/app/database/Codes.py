import sqlite3
import json

from app.config import config


class Codes:
    """
    A class that allows for interaction with the Codes in the database
    """

    def __init__(self, database_name: str) -> None:
        """
        Code constructor. Creates the Code table if the table does not yet exist, otherwise does nothing.
        """
        self.db_name = database_name
        self._create_table()

    def _create_table(self) -> None:
        """
        Private method. Creates the Code table if it does not yet exist, otherwise does nothing.
        """
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {config.DB_CODE_TABLE_NAME} (
                    code_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    name TEXT NOT NULL UNIQUE,
                    quotes TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

    def insert(self, code_name: str, quotes: list, project_id: str) -> int:
        """
        Method to insert codes into the table. Returns the id of the code on success, and None on failure.

        Args:
            code_name (str): The name of the code. Must be unique or else it will fail on insert
            quotes (list): The quotes associated with the code

        Returns:
            int: The code id on successful insert, or None on failure.
        """
        code_id = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                INSERT INTO {config.DB_CODE_TABLE_NAME} (name, quotes, project_id) VALUES (?, ?, ?)
            """,
                (code_name, json.dumps(quotes), project_id),
            )

            code_id = cur.lastrowid

        return code_id

    def update(self, code_id: int, code_name: str, quotes: list) -> int:
        """
        Method to update existing code in the table.

        Args:
            code_id (int): The id of the code.
            code_name (str): The name of the code. Must be unique or else it will fail on insert
            quotes (list): The quotes associated with the code
        """

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                UPDATE {config.DB_CODE_TABLE_NAME}
                SET name = ?, quotes = ?
                WHERE code_id = ?
            """,
                (code_name, json.dumps(quotes), code_id),
            )

            if cur.rowcount < 1:
                raise ValueError("There is no row associated with this code id!")

    def delete(self, code_id: int):
        """
        Method to delete code from table. Will also delete all associated transcriptions

        Args:
            code_id (int): code id to delete

        Raises:
            ValueError: If there is no row associated with the code id, then a ValueError is raised
        """
        rows_deleted = 0
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                DELETE FROM {config.DB_CODE_TABLE_NAME}
                WHERE code_id = ? 
            """,
                (code_id,),
            )

            rows_deleted = cur.rowcount

        if rows_deleted < 1:
            raise ValueError("There is no row associated with this code id!")

    def get_code_by_id(self, code_id: int) -> tuple[str, str, str]:
        """
        Method to get code data by its id.

        Args:
            code_id (int): The id of the code

        Returns:
            tuple[str, str, str]: The code name, quotes and creation date

        Raises:
            LookupError: If there is no code with the given id, raises LookupError
        """
        code = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT name, quotes, created_at FROM {config.DB_CODE_TABLE_NAME}
                WHERE code_id = ?
            """,
                (code_id,),
            )

            row = cur.fetchone()

        if row is None:
            raise LookupError("There is no code with that id!")

        name, quotes_json, created_at = row
        return [name, json.loads(quotes_json), created_at]

    def get_all_codes(self) -> list[tuple[int, str, str, str]]:
        """
        Method to get all codes that exist.

        Returns:
            list[tuple[int, str, str, str]]: The code id, name quotes and creation date for each code
        """
        codes = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT code_id, name, quotes, created_at FROM {config.DB_CODE_TABLE_NAME}
            """
            )

            rows = cur.fetchall()

        return [
            (code_id, name, json.loads(quotes_json), created_at)
            for code_id, name, quotes_json, created_at in rows
        ]

    def get_codes_by_project(self, project_id: int) -> list[tuple[int, str, list, str]]:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT code_id, name, quotes, created_at
                FROM {config.DB_CODE_TABLE_NAME}
                WHERE project_id = ?
            """,
                (project_id,),
            )

            rows = cur.fetchall()

        return [
            (code_id, name, json.loads(quotes_json), created_at)
            for code_id, name, quotes_json, created_at in rows
        ]

    def clear_codes_by_project(self, project_id: int) -> list[tuple[int, str, list, str]]:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                DELETE FROM {config.DB_CODE_TABLE_NAME}
                WHERE project_id = ?
            """,
                (project_id,),
            )

            rows = cur.fetchall()