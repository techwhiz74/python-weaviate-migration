import os
import sys
import tempfile
import subprocess
from django.test import TestCase
import django
from django.conf import settings, Settings, LazySettings  
from django.db import models
from weaviate_migrate.commands.django_makemigrations import generate_weaviate_schema_from_django_models, main
import argparse


class TestWeaviateMigrate(TestCase):

    # @classmethod  
    # def setUpTestData(cls):  
    #     super().setUpTestData()  
    #     os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'  
    #     django.setup()  
  
    def setUp(self):  
        # Setup a temporary Weaviate instance using Docker  
        self.temp_dir = tempfile.mkdtemp()  
        self.weaviate_process = subprocess.Popen(  
            ["docker", "run", "--rm", "-d", "-p", "8080:8080",  
             "semitechnologies/weaviate:latest"],  
            cwd=self.temp_dir,  
            stdout=subprocess.PIPE,  
            stderr=subprocess.PIPE,  
        )  
  
    def tearDown(self):  
        migration_path = os.path.join(self.temp_dir, "0001_migration.json")
        if os.path.exists(migration_path):
            os.remove(migration_path) # Delete the migration file
        self.weaviate_process.terminate()  
        self.weaviate_process.wait(timeout=5) 
        self.weaviate_process.kill()
        os.rmdir(self.temp_dir)  

    def test_cross_references(self):

        if not self.target_schema:
            print("Target schema is empty, skipping test")
            return 
        # Define test models
        class SourceClass(models.Model):
            name = models.CharField(max_length=100)

        class TargetClass(models.Model):
            name = models.CharField(max_length=100)

        class AnotherSourceClass(models.Model):
            name = models.CharField(max_length=100)

        class AnotherTargetClass(models.Model):
            name = models.CharField(max_length=100)

        model_prefix = "Test"

        # Add ForeignKey and ManyToManyField to test models
        SourceClass.add_to_class(
            'hasParagraphs', models.ManyToManyField(TargetClass))
        AnotherSourceClass.add_to_class('relatedItem', models.ForeignKey(
            AnotherTargetClass, on_delete=models.CASCADE))

        # Generate Weaviate schema from Django models
        weaviate_schema = generate_weaviate_schema_from_django_models(model_prefix)

        # Check if cross references are added correctly
        for weaviate_class in weaviate_schema:
            if weaviate_class["class"] == "SourceClass":
                self.assertEqual(len(weaviate_class["properties"]), 2)
                self.assertIn({"name": "hasParagraphs", "type": "cref", "cardinality": "many", "refClass": "TargetClass"},
                              weaviate_class["properties"])
            elif weaviate_class["class"] == "AnotherSourceClass":
                self.assertEqual(len(weaviate_class["properties"]), 2)
                self.assertIn({"name": "relatedItem", "type": "cref", "cardinality": "toOne", "refClass": "AnotherTargetClass"},
                              weaviate_class["properties"])

        # Test the main function  
        original_argv = sys.argv  
        sys.argv = [  
            "test_script",  
            "--url", "http://localhost:8080",  
            "--api-key", "",  
            "--folder", self.temp_dir,  
            "--django-settings", "django.conf.settings",  
            "--model-prefix", "Test"
        ]  
    
        try:  
            main()  
        except Exception as e:  
            self.fail(f"Exception occurred: {e}")  
        finally:  
            sys.argv = original_argv  
