import sqlite3


class ChatHistory:
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
                """
                CREATE TABLE IF NOT EXISTS project_chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    sender TEXT NOT NULL CHECK (sender IN ('user','ai')),
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES project(project_id) ON DELETE CASCADE
                )
                """
            )

    def insert(self, project_id: int, sender: str, message: str) -> int:
        """
        Method to add a chat message row for the given project.

        Args:
            project_id (int): project id for the associated project
            sender (str): who sent the message, one of 'user' or 'ai'
            message (str): the chat message text

        Returns:
            int: The message id on successful insert
        """
        message_id = None
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")
            cur.execute(
                """
                INSERT INTO project_chat_messages (project_id, sender, text)
                VALUES (?, ?, ?)
                """,
                (project_id, sender, message),
            )
            message_id = cur.lastrowid

        return message_id

    def get_all_project_chat_messages(self, project_id: int) -> list[tuple[int, str, str, str]]:
        """
        Method to list chat messages for a project, ordered by time.

        Returns:
            list[tuple[int, str, str, str]]: (message_id, sender, text, created_at)
        """
        messages: list[tuple[int, str, str, str]] = []

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")
            cur.execute(
                """
                SELECT id, sender, text, created_at
                FROM project_chat_messages
                WHERE project_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (project_id,),
            )
            messages = cur.fetchall()

        return messages

    def delete(self, message_id: int, project_id: int) -> None:
        """
        Method to delete a chat message from table.

        Args:
            message_id (int): Message id to delete
            project_id (int): Project id for verification

        Raises:
            ValueError: If there is no row associated with the message id, raises ValueError
        """
        rows_deleted = 0
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")
            cur.execute(
                """
                DELETE FROM project_chat_messages
                WHERE id = ? AND project_id = ?
                """,
                (message_id, project_id),
            )
            rows_deleted = cur.rowcount

        if rows_deleted < 1:
            raise ValueError("There is no chat message associated with this id or project!")
