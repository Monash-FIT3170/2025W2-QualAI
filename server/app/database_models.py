import sqlite3
from typing import Optional

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
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {PROJECT_TABLE_NAME} (
                        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        description TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

        except sqlite3.Error as e:
            print(f"There was an error creating the table: {e}")

    def insert(self, project_name: str, description: str = "") -> Optional[int]:
        """
        Method to insert propject into the table. Returns the id of the project on success, and None on failure.

        Args:
            project_name (str): The name of the project. Must be unique or else it will fail on insert
            description (str): The description of the project

        Returns:
            Optional int: The project id on successful insert, or None on failure.
        """
        try:
            project_id = None

            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    INSERT INTO {PROJECT_TABLE_NAME} (name, description) VALUES (?, ?)
                """, (project_name, description))

                project_id =  cur.lastrowid

            return project_id

        except sqlite3.Error as e:
            print(f"There was an error inserting into the table: {e}")
            return None

    def delete(self, project_id: int) -> bool:
        """
        Method to delete project from table. Will also delete all associated transcriptions

        Args:
            project_id (int): project id to delete

        Returns:
            bool: True on successful delete, False on failure
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    DELETE FROM {PROJECT_TABLE_NAME}
                    WHERE project_id = ? 
                """, (project_id,))

            return True

        except sqlite3.Error as e:
            print(f"There was an error deleting the project: {e}")
            return False
    
    def get_project_by_id(self, project_id: int) -> Optional[tuple[str, str, str]]:
        """
        Method to get project data by its id.

        Args:
            transcription_id (int): The id of the project

        Returns:
            Optional tuple[str, str, str]: The project name, description and creation date
        """
        try:
            project = None

            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    SELECT name, description, created_at FROM {PROJECT_TABLE_NAME}
                    WHERE project_id = ?
                """, (project_id,))

                project = cur.fetchone()

            return project

        except sqlite3.Error as e:
            print(f"There was an error getting the project: {e}")
            return None

    def get_all_projects(self) -> Optional[list[tuple[int, str, str, str]]]:
        """
        Method to get all projects that exist.

        Returns:
            Optional list[tuple[int, str, str, str]]: The project id, name description and creation date for each project
        """
        try:
            projects = None

            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    SELECT project_id, name, description, created_at FROM {PROJECT_TABLE_NAME}
                """)

                projects = cur.fetchall()

            return projects

        except sqlite3.Error as e:
            print(f"There was an error getting the projects: {e}")
            return None
        
    def drop_table(self):
        """
        Dev method, should not be kept in final version!!
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    DROP TABLE IF EXISTS {PROJECT_TABLE_NAME};
                """)

            return None

        except sqlite3.Error as e:
            print(f"There was an error getting the projects: {e}")
            return None



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
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {TRANS_TABLE_NAME} (
                        transcription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER,
                        name TEXT NOT NULL,
                        transcription TEXT NOT NULL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES {PROJECT_TABLE_NAME}(project_id) ON DELETE CASCADE
                    )
                """)
        except sqlite3.Error as e:
            print(f"There was an error creating the table: {e}")

    def insert(self, project_id: int, name: str, transcription: str) -> Optional[int]:
        """
        Method to insert transcription into the table. Returns the id of the transcription on success, and None on failure.

        Args:
            project_id (int): The id of the project associated with the transcription
            name (str): The name of the transcription
            transcription (str): The transcription for the audio

        Returns:
            Optional int: The transcription id on successful insert, or None on failure.
        """
        try:
            transcription_id = None

            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    INSERT INTO {TRANS_TABLE_NAME} (project_id, name, transcription) VALUES (?, ?, ?)
                """, (project_id, name, transcription))

                transcription_id = cur.lastrowid 

            return transcription_id

        except sqlite3.Error as e:
            print(f"There was an error inserting into the table: {e}")
            return None
        
    def delete(self, transcription_id: int) -> bool:
        """
        Method to delete transcription from table.

        Args:
            transcription_id (int): Transcription id to delete

        Returns:
            bool: True on successful delete, False on failure
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    DELETE FROM {TRANS_TABLE_NAME}
                    WHERE transcription_id = ?
                """, (transcription_id,))

            return True

        except sqlite3.Error as e:
            print(f"There was an error deleting the transcription: {e}")
            return False
        
    def get_transcription_by_id(self, transcription_id: int) -> Optional[tuple[int, str, str, str]]:
        """
        Method to get transcriptions data by its id.

        Args:
            transcription_id (int): The id of the transcription

        Returns:
            Optional tuple[int, str, str, str]: The transcription id, name, transcription text and process date
        """
        try:
            transcription = None

            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    SELECT project_id, name, transcription, processed_at FROM {TRANS_TABLE_NAME}
                    WHERE transcription_id = ?
                """, (transcription_id,))

                transcription = cur.fetchone()

            return transcription

        except sqlite3.Error as e:
            print(f"There was an error getting the transcription: {e}")

    def get_all_project_transcriptions(self, project_id: int) -> Optional[list[tuple[int, str, str]]]:
        """
        Method to get all transcriptions associated with a project. Crucially, it does not return the transcription text itself.

        Args:
            project_id (int): The id of the project

        Returns:
            Optional list[tuple[int, str, str]]: The transcription id, name and process date for each transcription associated with the project
        """
        try:
            transcriptions = None

            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    SELECT transcription_id, name, processed_at FROM {TRANS_TABLE_NAME}
                    WHERE project_id = ?
                """, (project_id,))

                transcriptions = cur.fetchall()

            return transcriptions

        except sqlite3.Error as e:
            print(f"There was an error getting the project transcriptions: {e}")

    def drop_table(self):
        """
        Dev method, should not be kept in final version!!
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")

                cur.execute(f"""
                    DROP TABLE {TRANS_TABLE_NAME};
                """)

            return None

        except sqlite3.Error as e:
            print(f"There was an error getting the projects: {e}")
            return None
        