import os
import json
from weaviate import Client
import argparse

def load_migration(migration_path):
    """
    Load a migration file.
    """
    with open(migration_path, 'r') as f:
        return json.load(f)

def apply_migration(client, schema):  
    """  
    Apply a migration to the Weaviate instance.  
    """  
    current_schema = client.schema.get()  
  
    for class_definition in schema['classes']:  
        class_name = class_definition['class']  
        if not any(c['class'] == class_name for c in current_schema['classes']):  
            client.schema.create_class(class_definition)  
            print(f"Created class: {class_name}")  
  
        for property_definition in class_definition['properties']:  
            property_name = property_definition['name']  
            if not any(any(p['name'] == property_name for p in c['properties']) for c in current_schema['classes']):  
                client.schema.create_property(class_name, property_definition)  
                print(f"Created property: {property_name}")  


def migrate(client, migration_folder):  
    """
    Apply all migration files to the Weaviate instance.
    """

    if not os.path.exists(migration_folder):
        print(f"Migration folder '{migration_folder}' does not exist.")
        return

    migration_files = sorted(os.listdir(migration_folder))

    for migration_file in migration_files:
        migration_path = os.path.join(migration_folder, migration_file)
        schema = load_migration(migration_path)
        apply_migration(client, schema)
        print(f"Applied migration: {migration_file}")

def main():
    parser = argparse.ArgumentParser(description="Weaviate schema migration tool.")
    parser.add_argument("--url", required=True, default="http://localhost:8080", help="Weaviate URL.")
    parser.add_argument("--folder", default="migrations", help="Path to the migration folder.")
    parser.add_argument("--api-key", help="Weaviate API key (optional).")  
    parser.add_argument("--api-token", help="Weaviate API token (optional).")  
    args = parser.parse_args()

    # Set up the Weaviate client  
    client = Client(args.url, api_key=args.api_key)  
    if args.api_key and args.api_token:  
        client.authenticate(args.api_key, args.api_token)  

    migrate(client, args.folder)  

if __name__ == "__main__":
    main()