import sqlite3
from app.config import config


class Highlighter:
    """
    A class that allows for interaction with the highlighters in the database.
    """

    def __init__(self, database_name: str) -> None:
        """
        Highlighter constructor. Creates the highlighters table if the table does not yet exist, otherwise does nothing.
        """
        self.db_name = database_name
        self._create_table()

    def _create_table(self) -> None:
        """
        Private method. Creates the highlighters table if it does not yet exist, otherwise does nothing.
        """
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {config.DB_HIGHLIGHTER_TABLE_NAME} (
                    highlighter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    label TEXT NOT NULL,
                    colour TEXT NOT NULL,
                    weight TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES {config.DB_PROJECT_TABLE_NAME}(project_id)
                        ON DELETE CASCADE
                )
                """
            )

    def insert(self, project_id: int, label: str, colour: str, weight: str) -> int:
        """
        Method to insert a highlighter into the table. Returns the id of the highlighter on success.

        Args:
            project_id (int): The id of the project the highlighter belongs to.
            label (str): The label of the highlighter.
            colour (str): The colour of the highlighter (hex or rgba).
            weight (str): The weight of the highlighter.

        Returns:
            int: The highlighter id on successful insert.
        """
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                INSERT OR IGNORE INTO {config.DB_HIGHLIGHTER_TABLE_NAME} (project_id, label, colour, weight)
                VALUES (?, ?, ?, ?)
                """,
                (project_id, label, colour, weight),
            )

            highlighter_id = cur.lastrowid

        return highlighter_id

    def delete(self, highlighter_id: int) -> None:
        """
        Method to delete a highlighter from the table.

        Args:
            highlighter_id (int): The id of the highlighter to delete.

        Raises:
            ValueError: If there is no row associated with the highlighter id, then a ValueError is raised.
        """
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                DELETE FROM {config.DB_HIGHLIGHTER_TABLE_NAME}
                WHERE highlighter_id = ?
                """,
                (highlighter_id,),
            )

            if cur.rowcount < 1:
                raise ValueError("There is no row associated with this highlighter id!")

    def update(self, highlighter_id: int, **kwargs) -> None:
        """
        Method to update a highlighter's properties.

        Args:
            highlighter_id (int): The id of the highlighter to update.
            kwargs: Key-value pairs of columns to update.

        Raises:
            ValueError: If there is no highlighter with the given id.
        """
        if not kwargs:
            return

        columns = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [highlighter_id]

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                UPDATE {config.DB_HIGHLIGHTER_TABLE_NAME}
                SET {columns}, updated_at = CURRENT_TIMESTAMP
                WHERE highlighter_id = ?
                """,
                values,
            )

            if cur.rowcount < 1:
                raise ValueError("There is no row associated with this highlighter id!")

    def get_highlighter_by_id(
        self, highlighter_id: int
    ) -> tuple[int, str, str, str, str, str]:
        """
        Method to get highlighter data by its id.

        Args:
            highlighter_id (int): The id of the highlighter.

        Returns:
            tuple[int, str, str, str, str, str]: The project_id, label, colour, created_at, and updated_at.

        Raises:
            LookupError: If there is no highlighter with the given id.
        """
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT project_id, label, colour, weight, created_at, updated_at
                FROM {config.DB_HIGHLIGHTER_TABLE_NAME}
                WHERE highlighter_id = ?
                """,
                (highlighter_id,),
            )

            highlighter = cur.fetchone()

        if highlighter is None:
            raise LookupError("There is no highlighter with that id!")

        return highlighter

    def get_highlighters_by_project(
        self, project_id: int
    ) -> list[tuple[int, str, str, str, str, str]]:
        """
        Method to get all highlighters associated with a specific project.

        Args:
            project_id (int): The id of the project.

        Returns:
            list[tuple[int, str, str, str, str, str]]: A list of tuples containing
                (highlighter_id, label, colour, weight, created_at, updated_at)
        """
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT highlighter_id, label, colour, weight, created_at, updated_at
                FROM {config.DB_HIGHLIGHTER_TABLE_NAME}
                WHERE project_id = ?
                ORDER BY created_at ASC
                """,
                (project_id,),
            )

            highlighters = cur.fetchall()

        return highlighters
