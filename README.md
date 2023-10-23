# Weaviate Migrate

Weaviate Migrate is a tool to handle schema migrations for Weaviate. This project allows you to create and apply migration files to manage your Weaviate schema.

## Features

- Create and apply migration files for Weaviate schema changes
- Manage schema updates in a structured and organized manner
- Easy-to-use command-line interface

## Installation

Clone the repository:

```
git clone https://github.com/TonyLLondon/weaviate-migrate.git
```

To install Weaviate Migrate, run the following command:

```bash
pip install -e .
```

This will install the required dependencies and make the `weaviate-makemigrations` and `weaviate-migrate` commands available in your environment.

## Usage

### Creating Migrations

To create a new migration file with the current Weaviate schema, run the following command:

```bash
weaviate-makemigrations
```

This will create a new migration file in the `migrations` folder.

### Applying Migrations

To apply all migration files to the Weaviate instance, run the following command:

```bash
weaviate-migrate
```

This will apply all migration files in the `migrations` folder to your Weaviate instance.

## Testing

To run the tests for this project, execute the following command:

```bash
pytest tests/
```

## Contributing

We welcome contributions to this project! Please feel free to open issues or submit pull requests with improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.