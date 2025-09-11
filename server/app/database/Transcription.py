import sqlite3
from typing import List, Tuple, Optional

from app.config import config


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
                CREATE TABLE IF NOT EXISTS {config.DB_TRANS_TABLE_NAME} (
                    transcription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    name TEXT NOT NULL,
                    transcription TEXT NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES {config.DB_PROJECT_TABLE_NAME}(project_id) ON DELETE CASCADE
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
                INSERT INTO {config.DB_TRANS_TABLE_NAME} (project_id, name, transcription) VALUES (?, ?, ?)
            """,
                (project_id, name, transcription),
            )

            transcription_id = cur.lastrowid

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
                DELETE FROM {config.DB_TRANS_TABLE_NAME}
                WHERE transcription_id = ?
            """,
                (transcription_id,),
            )

            rows_deleted = cur.rowcount

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
                SELECT project_id, name, transcription, processed_at FROM {config.DB_TRANS_TABLE_NAME}
                WHERE transcription_id = ?
            """,
                (transcription_id,),
            )

            transcription = cur.fetchone()

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
                SELECT transcription_id, name, processed_at FROM {config.DB_TRANS_TABLE_NAME}
                WHERE project_id = ?
            """,
                (project_id,),
            )

            transcriptions = cur.fetchall()

        return transcriptions

    def update(self, transcription_id: int, transcription_text: str) -> bool:
        """
        Method to update transcription text by its id.

        Args:
            transcription_id (int): The id of the transcription to update
            transcription_text (str): The new transcription text

        Returns:
            bool: True if update was successful, False otherwise

        Raises:
            ValueError: If there is no row associated with the transcription id
        """
        rows_updated = 0

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")

            cur.execute(
                f"""
                UPDATE {config.DB_TRANS_TABLE_NAME}
                SET transcription = ?, processed_at = CURRENT_TIMESTAMP
                WHERE transcription_id = ?
            """,
                (transcription_text, transcription_id),
            )

            rows_updated = cur.rowcount

        if rows_updated < 1:
            raise ValueError("There is no row associated with this transcription id!")

        return True
