import sqlite3
from typing import Tuple, List, Dict, Optional

PROJECT_TABLE_NAME = "project"
TRANS_TABLE_NAME = "transcription"


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
                CREATE TABLE IF NOT EXISTS {PROJECT_TABLE_NAME} (
                    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

    def update(self, old_project_name: str, project_name: str, description) -> int:
        """
        Method to update project name and description. Returns the id of the project on success, and None on failure.

        Args:
            old_project_name (str): The old name of the project.Must be existing in the databaase or else it will fail.
            project_name (str): The new name of the project. Must be unique or else it will fail.
            description (str): The new description of the project

        Returns:
            int: The project id on successful insert, or None on failure.
        """
        project_id = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                UPDATE {PROJECT_TABLE_NAME} 
                SET name = ?, description = ? 
                WHERE name = ?
            """,
                (project_name, description, old_project_name),
            )

            project_id = cur.lastrowid
            conn.commit()

        return project_id

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
                INSERT INTO {PROJECT_TABLE_NAME} (name, description) VALUES (?, ?)
            """,
                (project_name, description),
            )

            project_id = cur.lastrowid
            conn.commit()

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
                DELETE FROM {PROJECT_TABLE_NAME}
                WHERE project_id = ? 
            """,
                (project_id,),
            )

            rows_deleted = cur.rowcount
            conn.commit()

        if rows_deleted < 1:
            raise ValueError("There is no row associated with this project id!")

    def get_project_by_id(self, project_id: int) -> Tuple[str, str, str]:
        """
        Method to get project data by its id.

        Args:
            transcription_id (int): The id of the project

        Returns:
            Tuple[str, str, str]: The project name, description and creation date

        Raises:
            LookupError: If there is no project with the given id, raises LookupError
        """
        project = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT name, description, created_at FROM {PROJECT_TABLE_NAME}
                WHERE project_id = ?
            """,
                (project_id,),
            )

            project = cur.fetchone()

        if project is None:
            raise LookupError("There is no project with that id!")

        return project

    def get_all_projects(self) -> List[Tuple[int, str, str, str]]:
        """
        Method to get all projects that exist.

        Returns:
            List[Tuple[int, str, str, str]]: The project id, name description and creation date for each project
        """
        projects = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT project_id, name, description, created_at FROM {PROJECT_TABLE_NAME}
            """
            )

            projects = cur.fetchall()

        return projects


class Transcription:
    """
    A class that allows for interaction with the transcriptions in the database
    """

    def __init__(self, database_name: str) -> None:
        """
        Transcription constructor. Creates the transcription table if the table does not yet exist, otherwise does nothing.
        """
        self.db_name = database_name
        self._create_table()

    def _create_table(self) -> None:
        """
        Private method. Creates the transcription table if it does not yet exist, otherwise does nothing.
        """
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TRANS_TABLE_NAME} (
                    transcription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    name TEXT NOT NULL,
                    transcription TEXT NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES {PROJECT_TABLE_NAME}(project_id) ON DELETE CASCADE
                )
            """
            )

    def insert(self, project_id: int, name: str, transcription: str) -> Optional[int]:
        """
        Method to insert transcription into the table. Returns the id of the transcription on success, and None on failure.

        Args:
            project_id (int): The id of the project associated with the transcription
            name (str): The name of the transcription
            transcription (str): The transcription for the audio

        Returns:
            int: The transcription id on successful insert, or None on failure.
        """
        transcription_id = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                INSERT INTO {TRANS_TABLE_NAME} (project_id, name, transcription) VALUES (?, ?, ?)
            """,
                (project_id, name, transcription),
            )

            transcription_id = cur.lastrowid
            conn.commit()

        return transcription_id

    def delete(self, transcription_id: int):
        """
        Method to delete transcription from table.

        Args:
            transcription_id (int): Transcription id to delete

        Raises:
            ValueError: If there is no row associated with the transcription id, raises ValueError
        """
        rows_deleted = 0
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                DELETE FROM {TRANS_TABLE_NAME}
                WHERE transcription_id = ?
            """,
                (transcription_id,),
            )

            rows_deleted = cur.rowcount
            conn.commit()

        if rows_deleted < 1:
            raise ValueError("There is no row associated with this transcription id!")

    def get_transcription_by_id(
        self, transcription_id: int
    ) -> Tuple[int, str, str, str]:
        """
        Method to get transcriptions data by its id.

        Args:
            transcription_id (int): The id of the transcription

        Returns:
            Tuple[int, str, str, str]: The transcription id, name, transcription text and process date
        """
        transcription = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT project_id, name, transcription, processed_at FROM {TRANS_TABLE_NAME}
                WHERE transcription_id = ?
            """,
                (transcription_id,),
            )

            transcription = cur.fetchone()
            conn.commit()

        if transcription is None:
            raise LookupError("There is no transcription with that id!")

        return transcription

    def get_all_project_transcriptions(
        self, project_id: int
    ) -> List[Tuple[int, str, str]]:
        """
        Method to get all transcriptions associated with a project. Crucially, it does not return the transcription text itself.

        Args:
            project_id (int): The id of the project

        Returns:
            List[Tuple[int, str, str]]: The transcription id, name and process date for each transcription associated with the project
        """
        transcriptions = None

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                SELECT transcription_id, name, processed_at FROM {TRANS_TABLE_NAME}
                WHERE project_id = ?
            """,
                (project_id,),
            )

            transcriptions = cur.fetchall()
            conn.commit()

        return transcriptions


# if __name__ == "__main__":
#     project_manager = Project("qualAI_test.db")
#     project_name = "unique_project_4"
#     inserted_id = project_manager.insert(project_name, "To be deleted")
#     print(inserted_id)
#     deletion_successful = project_manager.delete(inserted_id)
#     print(deletion_successful)

#     project_manager.get_project_by_id(inserted_id)
