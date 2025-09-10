import os
import tempfile
from app.database import Project

import unittest
from sqlite3 import IntegrityError


class Test_Project(unittest.TestCase):

    def setUp(self):
        """Set up for each test - ensures a clean database."""
        self.db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_name = self.db.name
        self.db.close()
        self.project_manager = Project(self.db_name)

    # def tearDown(self):
    #     if os.path.exists(self.db_name):
    #         os.remove(self.db_name)

    def test_valid_insert_project(self):
        project_name = "unique_project_1"
        description = "A test project"
        res = self.project_manager.insert(project_name, description)
        self.assertIsInstance(res, int)

    def test_invalid_insert_project(self):
        with self.assertRaises(IntegrityError):
            self.project_manager.insert(None, None)

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
        inserted_id = self.project_manager.insert(
            project_name, "Yet another description"
        )
        self.assertIsNotNone(inserted_id)
        non_existent_id = inserted_id + 100
        with self.assertRaises(LookupError):
            self.project_manager.get_project_by_id(non_existent_id)

    def test_delete_project(self):
        project_name = "unique_project_4"
        inserted_id = self.project_manager.insert(project_name, "To be deleted")
        self.assertIsNotNone(inserted_id)
        self.project_manager.delete(inserted_id)

        with self.assertRaises(LookupError):
            self.project_manager.get_project_by_id(inserted_id)

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
