import os  
import sys  
import argparse  
from weaviate_migrate.commands.makemigrations import make_migrations  
from weaviate import Client
import weaviate

def django_field_to_weaviate_type(field):  
    """  
    Convert a Django field type to a Weaviate data type.  
    """  
    type_mapping = {  
        'CharField': 'string',  
        'TextField': 'text',  
        'IntegerField': 'int',  
        'BigIntegerField': 'int',  # Weaviate 'int' can handle both IntegerField and BigIntegerField ranges  
        'SmallIntegerField': 'int',  
        'PositiveIntegerField': 'int',  
        'PositiveSmallIntegerField': 'int',  
        'FloatField': 'number',  
        'DecimalField': 'number',  
        'BooleanField': 'boolean',  
        'NullBooleanField': 'boolean',  
        'DateField': 'date',  
        'DateTimeField': 'date',  # Weaviate 'date' can handle both DateField and DateTimeField  
        'TimeField': 'string',  # Weaviate does not have a dedicated TimeField, so 'string' is a reasonable alternative  
        'EmailField': 'email',  
        'URLField': 'string',  
        'UUIDField': 'uuid',  
        'BinaryField': 'blob',  
        'ImageField': 'blob',  
        'FileField': 'blob',  
        'ForeignKey': 'cref',  # Requires additional handling for references  
        'OneToOneField': 'cref',  # Requires additional handling for references  
        'ManyToManyField': 'cref',  # Requires additional handling for references  
    }  

  
    field_type = field.get_internal_type()  
    if field_type in type_mapping:  
        return type_mapping[field_type]  
    else:  
        return 'string'  # Default to 'string' for unsupported field types   
  
def add_cross_references(weaviate_schema, cross_references):  
    for cross_reference in cross_references:  
        field_name = cross_reference['field_name']  
        source_class = cross_reference['source_class']  
        target_class = cross_reference['target_class']  
        cardinality = cross_reference['cardinality']  
  
        for weaviate_class in weaviate_schema:  
            if weaviate_class["class"] == source_class:  
                weaviate_property = {  
                    "name": field_name,  
                    "type": "cref",  
                    "cardinality": cardinality,  
                    "refClass": target_class  
                }  
                weaviate_class["properties"].append(weaviate_property)  
                break  



def generate_weaviate_schema_from_django_models(model_prefix):  
    from django.apps import apps  
  
    weaviate_schema = []  
  
    for model in apps.get_models():  
        if model.__module__ != __name__:  
            continue  

        # Check if model name starts with 'model_prefix'  
        if not model.__name__.startswith(model_prefix):  
            continue  

        weaviate_class = {  
            "class": model.__name__,  
            "properties": []  
        }  
  
        for field in model._meta.fields:  
            if field.get_internal_type() == "ForeignKey":  
                property_type = "cref"  
            else:  
                property_type = django_field_to_weaviate_type(field)  
  
            weaviate_property = {  
                "name": field.name,  
                "type": property_type  
            }  
            weaviate_class["properties"].append(weaviate_property)  
  
        weaviate_schema.append(weaviate_class)  
  
    return weaviate_schema  
  
  
def main():  
    parser = argparse.ArgumentParser(description="Create Weaviate migrations based on Django models.")  
    parser.add_argument("--url", required=True, help="Weaviate URL.")  
    parser.add_argument("--api-key", required=True, help="Weaviate API key.")  
    parser.add_argument("--folder", required=True, help="Migrations folder.")  
    parser.add_argument("--django-settings", required=True, help="Path to Django settings module.")  
    parser.add_argument("--model-prefix", required=True, help="Model prefix to designate weaviate models.")  
    args = parser.parse_args()  
  

    import django  
    django.setup()  
  
    # Generate Weaviate schema from Django models  
    weaviate_schema = generate_weaviate_schema_from_django_models(args.model_prefix)  

    cross_references = [  
        {  
            "field_name": "hasParagraphs",  
            "source_class": "SourceClass",  
            "target_class": "TargetClass",  
            "cardinality": "many"  
        },  
        {  
            "field_name": "relatedItem",  
            "source_class": "AnotherSourceClass",  
            "target_class": "AnotherTargetClass",  
            "cardinality": "toOne"  
        }  
    ]  

    # Add cross-references between classes  
    add_cross_references(weaviate_schema, cross_references)  

    if args.api_key:
        auth_config = weaviate.auth.AuthApiKey(
            api_key=args.api_key)

        client = Client(args.url, auth_client_secret=auth_config)  
    else:
        client = Client(args.url)
    
    # Create migrations based on the generated schema  
    make_migrations(client, args.folder, weaviate_schema)  
  
  
if __name__ == "__main__":  
    main()  
