import unittest
from os import remove
from app.database_models import Project, Transcription  # Make sure these are correctly imported

DB_NAME = "qualAI_test.db"
PROJECT_TABLE_NAME = "project"

class Test_Project(unittest.TestCase):
    def setUp(self):
        """Set up for each test - ensures a clean database."""
        try:
            remove(DB_NAME)
        except FileNotFoundError:
            pass
        self.project_manager = Project(DB_NAME)

    def test_insert_project(self):
        project_name = "unique_project_1"
        description = "A test project"
        res = self.project_manager.insert(project_name, description)
        self.assertIsInstance(res, int)

    def test_get_project_id_valid(self):
        project_name = "unique_project_2"
        description = "Another test project"
        inserted_id = self.project_manager.insert(project_name, description)
        self.assertIsNotNone(inserted_id)
        project = self.project_manager.get_project_by_id(inserted_id)
        self.assertIsNotNone(project)
        self.assertEqual(project[0], project_name)
        self.assertEqual(project[1], description)

    def test_get_project_by_id_not_found(self):
        project_name = "unique_project_3"
        inserted_id = self.project_manager.insert(project_name, "Yet another description")
        self.assertIsNotNone(inserted_id)
        non_existent_id = inserted_id + 100
        retrieved_project = self.project_manager.get_project_by_id(non_existent_id)
        self.assertIsNone(retrieved_project)

    def test_delete_project(self):
        project_name = "unique_project_4"
        inserted_id = self.project_manager.insert(project_name, "To be deleted")
        self.assertIsNotNone(inserted_id)
        deletion_successful = self.project_manager.delete(inserted_id)
        self.assertTrue(deletion_successful)
        retrieved_project = self.project_manager.get_project_by_id(inserted_id)
        self.assertIsNone(retrieved_project)

    def test_get_all_projects_empty(self):
        all_projects = self.project_manager.get_all_projects()
        self.assertEqual(all_projects, [])

    def test_get_all_projects_multiple(self):
        self.project_manager.insert("unique_project_5", "Description A")
        self.project_manager.insert("unique_project_6", "Description B")
        all_projects = self.project_manager.get_all_projects()
        self.assertEqual(len(all_projects), 2)
        names = {proj[1] for proj in all_projects}
        self.assertIn("unique_project_5", names)
        self.assertIn("unique_project_6", names)

class Test_Transcription(unittest.TestCase):
    def setUp(self):
        """Set up for each test ."""
        try:
            remove(DB_NAME)

        except FileNotFoundError:
            pass
        self.project_manager = Project(DB_NAME)
        self.transcription_manager = Transcription(DB_NAME)

        # Ensure there is atleast one project for transcription tests
        self.test_project_id = self.project_manager.insert("base_project_for_transcriptions", "Base project")
        self.assertIsNotNone(self.test_project_id, "Failed to create a base project for transcription tests")

    """Test to check if you can insert a transcription to the table"""
    def test_insert_transcription(self):
        name = "test_transcription_1"
        content = "This is a test transcription."
        res = self.transcription_manager.insert(self.test_project_id, name, content)
        self.assertIsInstance(res, int)

    """ Test to check a transcription is valid via its id"""
    def test_get_transcription_id_valid(self):
        name = "test_transcription_2"
        content = "Some content"
        inserted_id = self.transcription_manager.insert(self.test_project_id, name, content)
        self.assertIsNotNone(inserted_id)
        transcription = self.transcription_manager.get_transcription_by_id(inserted_id)
        self.assertIsNotNone(transcription)
        self.assertEqual(transcription[0], self.test_project_id) # Check project_id (index 0)
        self.assertEqual(transcription[1], name)  # Check name (index 1)
        self.assertEqual(transcription[2], content) # Check content (index 2)

    """ Test to check a transcription that doesnt exist via a non valid id"""
    def test_get_transcription_id_not_found(self):
        non_existent_id = 999
        retrieved_transcription = self.transcription_manager.get_transcription_by_id(non_existent_id)
        self.assertIsNone(retrieved_transcription)

    """ test to check valid deletion of transcription in table"""
    def test_delete_transcription(self):
        name = "test_transcription_3"
        content = "To be deleted."
        inserted_id = self.transcription_manager.insert(self.test_project_id, name, content)
        self.assertIsNotNone(inserted_id)
        deletion_successful = self.transcription_manager.delete(inserted_id)
        self.assertTrue(deletion_successful)
        retrieved_transcription = self.transcription_manager.get_transcription_by_id(inserted_id)
        self.assertIsNone(retrieved_transcription)

    def test_get_all_project_transcriptions_empty(self):
        transcriptions = self.transcription_manager.get_all_project_transcriptions(9999) # Non-existent project
        self.assertEqual(transcriptions, [])

    def test_get_all_project_transcriptions_multiple(self):
        self.transcription_manager.insert(self.test_project_id, "trans_a", "Content A")
        self.transcription_manager.insert(self.test_project_id, "trans_b", "Content B")
        transcriptions = self.transcription_manager.get_all_project_transcriptions(self.test_project_id)
        self.assertEqual(len(transcriptions), 2)
        names = {trans[1] for trans in transcriptions}
        self.assertIn("trans_a", names)
        self.assertIn("trans_b", names)

    def test_cascading_delete(self):
        project_id = self.project_manager.insert("unique_project_1", "A test project")
        self.transcription_manager.insert(project_id, "trans_a", "Content A")
        self.transcription_manager.insert(project_id, "trans_b", "Content B")

        # checking for succesful insert
        transcriptions = self.transcription_manager.get_all_project_transcriptions(project_id)
        self.assertEqual(len(transcriptions), 2)
        names = {trans[1] for trans in transcriptions}
        self.assertIn("trans_a", names)
        self.assertIn("trans_b", names)

        res = self.project_manager.delete(project_id)
        self.assertTrue(res)

        # transcriptions should be deleted when project is deleted

        res = self.transcription_manager.get_all_project_transcriptions(project_id)
        self.assertEqual(res, [])


if __name__ == '__main__':
    unittest.main()