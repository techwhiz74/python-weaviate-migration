import os
import json
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch
from weaviate_migrate.commands.migrate import migrate, load_migration, apply_migration


class TestMigrate(TestCase):

    @classmethod  
    def setUpClass(cls):  
        cls.temp_dir = tempfile.TemporaryDirectory()  
        cls.migration_folder = os.path.join(cls.temp_dir.name, "migrations")  


    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def create_migration_file(self, filename, content):  
        os.makedirs(self.migration_folder, exist_ok=True)  
        migration_path = os.path.join(self.migration_folder, filename)  
        with open(migration_path, "w") as f:  
            json.dump(content, f)  
        return migration_path  


    def test_load_migration(self):
        migration_content = {"classes": []}
        migration_path = self.create_migration_file("0001_migration.json", migration_content)

        loaded_migration = load_migration(migration_path)
        self.assertEqual(loaded_migration, migration_content)

    @patch("weaviate_migrate.commands.migrate.Client")
    def test_apply_migration(self, mock_client):
        schema = {
            "classes": [
                {
                    "class": "TestClass",
                    "properties": [
                        {
                            "name": "testProperty",
                            "dataType": ["string"]
                        }
                    ]
                }
            ]
        }

        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.schema.get.return_value = {"classes": []}

        apply_migration(mock_client_instance, schema)

        mock_client_instance.schema.create_class.assert_called_once_with(schema["classes"][0])
        mock_client_instance.schema.create_property.assert_called_once_with("TestClass", schema["classes"][0]["properties"][0])

    @patch("weaviate_migrate.commands.migrate.Client")
    def test_migrate(self, mock_client):
        migration_content = {"classes": []}
        self.create_migration_file("0001_migration.json", migration_content)

        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.schema.get.return_value = {"classes": []}

        migrate(mock_client_instance, self.migration_folder)  

        mock_client_instance.schema.get.assert_called_once()
        mock_client_instance.schema.create_class.assert_not_called()
        mock_client_instance.schema.create_property.assert_not_called()