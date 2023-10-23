import os
import json
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch
from weaviate_migrate.commands.makemigrations import make_migrations, get_schema, save_schema


class TestMakeMigrations(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.migration_folder = os.path.join(cls.temp_dir.name, "migrations")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    @patch("weaviate_migrate.commands.makemigrations.Client")
    def test_get_schema(self, mock_client):
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.schema.get.return_value = {"classes": []}

        schema = get_schema(mock_client_instance)
        self.assertEqual(schema, {"classes": []})
        mock_client_instance.schema.get.assert_called_once()

    def test_save_schema(self):
        schema = {"classes": []}
        migration_path = os.path.join(self.migration_folder, "0001_migration.json")

        if not os.path.exists(os.path.dirname(migration_path)):  
            os.makedirs(os.path.dirname(migration_path))  
        
        with open(migration_path, "w") as f:  
            pass  

        save_schema(schema, migration_path)

        with open(migration_path, "r") as f:
            saved_schema = json.load(f)

        self.assertEqual(saved_schema, schema)



    @patch("weaviate_migrate.commands.makemigrations.Client")
    def test_make_migrations(self, mock_client): 
        

        sample_target_schema = { 
            "classes": [
                { "class": "SampleClass", "properties": [
                    { "name": "sampleProperty", "dataType": ["string"] } 
                ]} 
            ] 
        }
        existing_schema = {
            "classes": []
        }
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.schema.get.return_value = existing_schema 
        
        expected_migration = {
            "classes_to_add": ["SampleClass"],
            "properties_to_add": {
                "SampleClass": ["sampleProperty"]
            }
        }
        
        make_migrations(mock_client_instance, self.migration_folder, sample_target_schema)
        
        migration_files = os.listdir(self.migration_folder)
        self.assertEqual(len(migration_files), 1)
        migration_path = os.path.join(self.migration_folder, migration_files[0])
        if not os.path.exists(os.path.dirname(migration_path)):
            os.makedirs(os.path.dirname(migration_path)) 
        with open(migration_path, "r") as f:
            actual_migration = json.load(f)
            
        self.assertEqual(actual_migration, expected_migration)