import os
import tempfile
from app.database import Project, Transcription

import unittest
from sqlite3 import IntegrityError


class Test_Transcription(unittest.TestCase):
    def setUp(self):
        """Set up for each test ."""
        self.db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_name = self.db.name
        self.db.close()
        self.project_manager = Project(self.db_name)
        self.transcription_manager = Transcription(self.db_name)

        # Ensure there is atleast one project for transcription tests
        self.test_project_id = self.project_manager.insert(
            "base_project_for_transcriptions", "Base project"
        )
        self.assertIsNotNone(
            self.test_project_id,
            "Failed to create a base project for transcription tests",
        )

    # TODO: fix teardown - temp files should not stay
    # def tearDown(self):
    #     if os.path.exists(self.db_name):
    #         os.remove(self.db_name)

    """Test to check if you can insert a transcription to the table"""

    def test_insert_transcription(self):
        name = "test_transcription_1"
        content = "This is a test transcription."
        res = self.transcription_manager.insert(self.test_project_id, name, content)
        self.assertIsInstance(res, int)

    def test_invalid_insert_transcription_values(self):
        with self.assertRaises(IntegrityError):
            self.transcription_manager.insert(self.test_project_id, None, None)

    def test_invalid_insert_transcription_proj_id(self):
        name = "test_transcription_1"
        content = "This is a test transcription."
        with self.assertRaises(IntegrityError):
            self.transcription_manager.insert(0, None, None)

    """ Test to check a transcription is valid via its id"""

    def test_get_transcription_id_valid(self):
        name = "test_transcription_2"
        content = "Some content"
        inserted_id = self.transcription_manager.insert(
            self.test_project_id, name, content
        )
        self.assertIsNotNone(inserted_id)
        transcription = self.transcription_manager.get_transcription_by_id(inserted_id)
        self.assertIsNotNone(transcription)
        # Check project_id (index 0)
        self.assertEqual(transcription[0], self.test_project_id)
        self.assertEqual(transcription[1], name)  # Check name (index 1)
        self.assertEqual(transcription[2], content)  # Check content (index 2)

    """ Test to check a transcription that doesnt exist via a non valid id"""

    def test_get_transcription_id_not_found(self):
        non_existent_id = 999
        with self.assertRaises(LookupError):
            self.transcription_manager.get_transcription_by_id(non_existent_id)

    """ test to check valid deletion of transcription in table"""

    def test_delete_transcription(self):
        name = "test_transcription_3"
        content = "To be deleted."
        inserted_id = self.transcription_manager.insert(
            self.test_project_id, name, content
        )
        self.assertIsNotNone(inserted_id)
        self.transcription_manager.delete(inserted_id)
        with self.assertRaises(LookupError):
            self.transcription_manager.get_transcription_by_id(inserted_id)

    def test_get_all_project_transcriptions_empty(self):
        transcriptions = self.transcription_manager.get_all_project_transcriptions(
            9999
        )  # Non-existent project
        self.assertEqual(transcriptions, [])

    def test_get_all_project_transcriptions_multiple(self):
        self.transcription_manager.insert(self.test_project_id, "trans_a", "Content A")
        self.transcription_manager.insert(self.test_project_id, "trans_b", "Content B")
        transcriptions = self.transcription_manager.get_all_project_transcriptions(
            self.test_project_id
        )
        self.assertEqual(len(transcriptions), 2)
        names = {trans[1] for trans in transcriptions}
        self.assertIn("trans_a", names)
        self.assertIn("trans_b", names)

    def test_cascading_delete(self):
        project_id = self.project_manager.insert("unique_project_1", "A test project")
        self.transcription_manager.insert(project_id, "trans_a", "Content A")
        self.transcription_manager.insert(project_id, "trans_b", "Content B")

        # checking for succesful insert
        transcriptions = self.transcription_manager.get_all_project_transcriptions(
            project_id
        )
        self.assertEqual(len(transcriptions), 2)
        names = {trans[1] for trans in transcriptions}
        self.assertIn("trans_a", names)
        self.assertIn("trans_b", names)

        self.project_manager.delete(project_id)

        # transcriptions should be deleted when project is deleted

        res = self.transcription_manager.get_all_project_transcriptions(project_id)
        self.assertEqual(res, [])
