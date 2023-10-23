import os
import json
from weaviate import Client
import argparse
from typing import Dict, List
import logging
logger = logging.getLogger(__name__)
MIGRATION_FILE_PATTERN = "{:04d}_migration.json"

def get_schema(client: Client) -> Dict:
    """
    Get the current schema from Weaviate.
    """
    return client.schema.get()


def save_schema(schema, migration_path):
    """
    Save the schema to a migration file.
    """
    with open(migration_path, "w") as f:
        json.dump(schema, f, indent=2)


def calculate_schema_diff(current_schema: Dict, target_schema: Dict) -> Dict:
    """Calculates the difference between two Weaviate schemas.

    Args:
        current_schema (Dict): The current Weaviate schema. Can be empty.
        target_schema (Dict): The target Weaviate schema. Can be empty.

    Returns:
        Dict: The schema diff containing:
            - classes_to_add: List of classes to add
            - classes_to_remove: List of classes to remove
            - properties_to_add: Dict of properties to add per class
            - properties_to_remove: Dict of properties to remove per class
            - properties_to_change: Dict of properties to change per class
    """
    migration_diff = {
        "classes_to_add": [],
        "classes_to_remove": [],
        "properties_to_add": {},
        "properties_to_remove": {},
        "properties_to_change": {},
    }

    # Handle empty current schema
    if not current_schema:
        migration_diff["classes_to_add"] = [
            c["class"] for c in target_schema["classes"]
        ]
        return migration_diff

    # Handle empty target schema
    if not target_schema:
        migration_diff["classes_to_remove"] = [
            c["class"] for c in current_schema["classes"]
        ]
        return migration_diff

    # Get all class names
    current_classes = {c["class"] for c in current_schema["classes"]}
    target_classes = {c["class"] for c in target_schema["classes"]}

    # Find classes to add and remove
    classes_to_add = target_classes - current_classes
    classes_to_remove = current_classes - target_classes
    migration_diff["classes_to_add"] = list(classes_to_add)
    migration_diff["classes_to_remove"] = list(classes_to_remove)

    # Get properties for all classes that exist in both schemas
    current_props = {
        c["class"]: c["properties"]
        for c in current_schema["classes"]
        if c["class"] in target_classes
    }
    target_props = {
        c["class"]: c["properties"]
        for c in target_schema["classes"]
        if c["class"] in target_classes
    }

    # Find properties to add, remove or change
    for class_name in target_classes & current_classes:
        current_class_props = {p["name"] for p in current_props[class_name]}
        target_class_props = {p["name"] for p in target_props[class_name]}

        props_to_add = target_class_props - current_class_props
        props_to_remove = current_class_props - target_class_props
        props_to_change = target_class_props & current_class_props

        migration_diff["properties_to_add"][class_name] = list(props_to_add)
        migration_diff["properties_to_remove"][class_name] = list(props_to_remove)
        migration_diff["properties_to_change"][class_name] = list(props_to_change)

    return migration_diff

def make_migrations(client, migration_folder: str, desired_schema: Dict) -> None:
    logger.info("Generating schema migration...")
    
    if not os.path.exists(migration_folder):
        raise ValueError(f"Migration folder {migration_folder} does not exist.")
    if not desired_schema:
        raise ValueError("Desired schema is empty.")
    
    try: 
        existing_schema = get_schema(client) 
    except Exception as e:
        logger.error(f"Could not get existing schema: {e}")
        raise e 
    
    migration_diff = calculate_schema_diff(existing_schema, desired_schema)
    
    migration_files = sorted(os.listdir(migration_folder))
    if migration_files:
        last_migration = migration_files[-1]
        last_migration_number = int(last_migration.split("_")[0]) 
    else: 
        last_migration_number = 0
        
    new_migration_number = last_migration_number + 1
    new_migration_filename = MIGRATION_FILE_PATTERN.format(new_migration_number)
    new_migration_path = os.path.join(migration_folder, new_migration_filename)
    
    save_schema(migration_diff, new_migration_path) 
    print(f"Created new migration file: {new_migration_path}")


def main():
    parser = argparse.ArgumentParser(description="Weaviate schema migration tool.")
    parser.add_argument("--url", default="http://localhost:8080", help="Weaviate URL.")
    parser.add_argument(
        "--folder", default="migrations", help="Path to the migration folder."
    )
    parser.add_argument("--api-key", help="Weaviate API key (optional).")
    parser.add_argument("--api-token", help="Weaviate API token (optional).")
    parser.add_argument("--target-schema-file", help="Path to the target schema file.")

    args = parser.parse_args()

    # Load the target schema from a file
    with open(args.target_schema_file, "r") as f:
        target_schema = json.load(f)

    # Set up the Weaviate client
    client = Client(args.url, auth_client_secret=args.api_token)

    make_migrations(client, args.folder, target_schema)


if __name__ == "__main__":
    main()

# import os
# import json
# from weaviate import Client
# import argparse
# from typing import Dict, List
# import logging

# logger = logging.getLogger(__name__)
# MIGRATION_FILE_PATTERN = "{:04d}_migration.json"

# def get_schema(client: Client) -> Dict:
#     """
#     Get the current schema from Weaviate.
#     """
#     return client.schema.get()


# def save_schema(schema, migration_path):
#     """
#     Save the schema to a migration file.
#     """
#     with open(migration_path, "w") as f:
#         json.dump(schema, f, indent=2)


# def calculate_schema_diff(current_schema: Dict, target_schema: Dict) -> Dict:
#     """Calculates the difference between two Weaviate schemas.

#     Args:
#         current_schema (Dict): The current Weaviate schema. Can be empty.
#         target_schema (Dict): The target Weaviate schema. Can be empty.

#     Returns:
#         Dict: The schema diff containing:
#             - classes_to_add: List of classes to add
#             - classes_to_remove: List of classes to remove
#             - properties_to_add: Dict of properties to add per class
#             - properties_to_remove: Dict of properties to remove per class
#             - properties_to_change: Dict of properties to change per class
#     """
#     migration_diff = {
#         "classes_to_add": [],
#         "classes_to_remove": [],
#         "properties_to_add": {},
#         "properties_to_remove": {},
#         "properties_to_change": {},
#     }

#     # Handle empty current schema
#     if not current_schema:
#         migration_diff["classes_to_add"] = [
#             c["class"] for c in target_schema["classes"]
#         ]
#         return migration_diff

#     # Handle empty target schema
#     if not target_schema:
#         migration_diff["classes_to_remove"] = [
#             c["class"] for c in current_schema["classes"]
#         ]
#         return migration_diff

#     # Get all class names
#     current_classes = {c["class"] for c in current_schema["classes"]}
#     target_classes = {c["class"] for c in target_schema["classes"]}

#     # Find classes to add and remove
#     classes_to_add = target_classes - current_classes
#     classes_to_remove = current_classes - target_classes
#     migration_diff["classes_to_add"] = list(classes_to_add)
#     migration_diff["classes_to_remove"] = list(classes_to_remove)

#     # Get properties for all classes that exist in both schemas
#     current_props = {
#         c["class"]: c["properties"]
#         for c in current_schema["classes"]
#         if c["class"] in target_classes
#     }
#     target_props = {
#         c["class"]: c["properties"]
#         for c in target_schema["classes"]
#         if c["class"] in target_classes
#     }

#     # Find properties to add, remove or change
#     for class_name in target_classes & current_classes:
#         current_class_props = {p["name"] for p in current_props[class_name]}
#         target_class_props = {p["name"] for p in target_props[class_name]}

#         props_to_add = target_class_props - current_class_props
#         props_to_remove = current_class_props - target_class_props
#         props_to_change = target_class_props & current_class_props

#         migration_diff["properties_to_add"][class_name] = list(props_to_add)
#         migration_diff["properties_to_remove"][class_name] = list(props_to_remove)
#         migration_diff["properties_to_change"][class_name] = list(props_to_change)

#     return migration_diff


# def make_migrations(client, migration_folder: str, desired_schema: Dict) -> None:
#     logger.info("Generating schema migration...")

#     if not os.path.exists(migration_folder):
#         raise ValueError(f"Migration folder {migration_folder} does not exist.")
#     if not desired_schema:
#         raise ValueError("Desired schema is empty.")

#     try:
#         existing_schema = get_schema(client)
#     except Exception as e:
#         logger.error(f"Could not get existing schema: {e}")
#         raise

#     migration_diff = calculate_schema_diff(existing_schema, desired_schema)

#     migration_files = sorted(os.listdir(migration_folder))
#     if migration_files:
#         last_migration = migration_files[-1]
#         last_migration_number = int(last_migration.split("_")[0])
#     else:
#         last_migration_number = 0

#     new_migration_number = last_migration_number + 1
#     new_migration_filename = MIGRATION_FILE_PATTERN.format(new_migration_number)
#     new_migration_path = os.path.join(migration_folder, new_migration_filename)

#     save_schema(migration_diff, new_migration_path)
#     print(f"Created new migration file: {new_migration_path}")


# def main():
#     parser = argparse.ArgumentParser(description="Weaviate schema migration tool.")
#     parser.add_argument("--url", default="http://localhost:8080", help="Weaviate URL.")
#     parser.add_argument("--folder", default="migrations", help="Path to the migration folder.")
#     parser.add_argument("--api-key", help="Weaviate API key (optional).")
#     parser.add_argument("--api-token", help="Weaviate API token (optional).")
#     parser.add_argument("--target-schema", help="Weaviate target schema.")
#     args = parser.parse_args()

#     if not args.target_schema:
#         raise ValueError("Target schema is required.")

#     target_schema = json.loads(args.target_schema)

#     # Set up the Weaviate client
#     client = Client(args.url, api_key=args.api_key)
#     if args.api_key and args.api_token:
#         client.authenticate(args.api_key, args.api_token)

#     make_migrations(client, args.folder, target_schema)


# if __name__ == "__main__":
#     main()



