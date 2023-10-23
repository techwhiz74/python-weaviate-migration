from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='weaviate-migrate',
    version='0.1',
    author="Tony Lewis",
    author_email="tony.lewis@gmail.com",
    description="A tool to handle schema migrations for Weaviate instances.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TonyLLondon/weaviate-migrate",
    packages=find_packages(),
    install_requires=[
        'weaviate-client',
        'django',
        'jsondiff',
        'jsonschema',
    ],
    extras_require={
        'test': [
            'pytest',
        ],
        'docs': [
            'mkdocs',
        ],
    },
    entry_points={
        'console_scripts': [
            'weaviate-makemigrations=weaviate_migrate.commands.makemigrations:main',
            'weaviate-migrate=weaviate_migrate.commands.migrate:main',
            'weaviate-django-makemigrations=weaviate_migrate.commands.django_makemigrations:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.6',
)
