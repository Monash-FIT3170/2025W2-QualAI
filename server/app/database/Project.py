import sqlite3

from app.config import config


class Project:
    """
    A class that allows for interaction with the projects in the database
    """

    def __init__(self, database_name: str) -> None:
        """
        Project constructor. Creates the projects table if the table does not yet exist, otherwise does nothing.
        """
        self.db_name = database_name
        self._create_table()

    def _create_table(self) -> None:
        """
        Private method. Creates the project table if it does not yet exist, otherwise does nothing.
        """
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {config.DB_PROJECT_TABLE_NAME} (
                    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

    def insert(self, project_name: str, description: str = "") -> int:
        """
        Method to insert propject into the table. Returns the id of the project on success, and None on failure.

        Args:
            project_name (str): The name of the project. Must be unique or else it will fail on insert
            description (str): The description of the project

        Returns:
            int: The project id on successful insert, or None on failure.
        """
        project_id = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                INSERT INTO {config.DB_PROJECT_TABLE_NAME} (name, description) VALUES (?, ?)
            """,
                (project_name, description),
            )

            project_id = cur.lastrowid

        return project_id

    def delete(self, project_id: int):
        """
        Method to delete project from table. Will also delete all associated transcriptions

        Args:
            project_id (int): project id to delete

        Raises:
            ValueError: If there is no row associated with the project id, then a ValueError is raised
        """
        rows_deleted = 0
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                DELETE FROM {config.DB_PROJECT_TABLE_NAME}
                WHERE project_id = ? 
            """,
                (project_id,),
            )

            rows_deleted = cur.rowcount

        if rows_deleted < 1:
            raise ValueError("There is no row associated with this project id!")

    def get_project_by_id(self, project_id: int) -> tuple[str, str, str]:
        """
        Method to get project data by its id.

        Args:
            transcription_id (int): The id of the project

        Returns:
            tuple[str, str, str]: The project name, description and creation date

        Raises:
            LookupError: If there is no project with the given id, raises LookupError
        """
        project = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT name, description, created_at FROM {config.DB_PROJECT_TABLE_NAME}
                WHERE project_id = ?
            """,
                (project_id,),
            )

            project = cur.fetchone()

        if project is None:
            raise LookupError("There is no project with that id!")

        return project

    def get_all_projects(self) -> list[tuple[int, str, str, str]]:
        """
        Method to get all projects that exist.

        Returns:
            list[tuple[int, str, str, str]]: The project id, name description and creation date for each project
        """
        projects = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT project_id, name, description, created_at FROM {config.DB_PROJECT_TABLE_NAME}
            """
            )

            projects = cur.fetchall()

        return projects
