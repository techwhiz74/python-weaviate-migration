from unittest import TestCase
from django.db import models 
from weaviate_migrate.commands.django_makemigrations import django_field_to_weaviate_type

class TestDjangoFieldToWeaviateType(TestCase):
    def test_charfield(self):
        field = models.CharField(max_length=100)
        weaviate_type = django_field_to_weaviate_type(field)
        self.assertEqual(weaviate_type, "string")
        
    def test_textfield(self):
        field = models.TextField()
        weaviate_type = django_field_to_weaviate_type(field)
        self.assertEqual(weaviate_type, "text")
        
    def test_integerfield(self):
        field = models.IntegerField()
        weaviate_type = django_field_to_weaviate_type(field)
        self.assertEqual(weaviate_type, "int")
        
    def test_booleanfield(self):
        field = models.BooleanField()
        weaviate_type = django_field_to_weaviate_type(field)
        self.assertEqual(weaviate_type, "boolean")
        
    def test_foreignkey(self):
        field = models.ForeignKey("self", on_delete=models.CASCADE)
        weaviate_type = django_field_to_weaviate_type(field)
        self.assertEqual(weaviate_type, "cref")
        
    def test_manytomanyfield(self):
        field = models.ManyToManyField("self")
        weaviate_type = django_field_to_weaviate_type(field)
        self.assertEqual(weaviate_type, "cref")