# FastAPI API

## Setup Instructions

1. **Python Version**: This project requires Python version 3.12.0.

2. **Create Virtual Environment (venv)**:
    ```bash
    python3 -m venv venv
    ```

3. **Install Poetry**:
    ```bash
    pip install poetry
    ```

4. **Install Dependencies**:
    ```bash
    poetry install
    ```

5. **Update Database Credentials**:
    Update the database credentials in the `int` environment before running the service.

6. **Database Migration**:
    - For upgrading migrations:
        ```bash
        poetry run alembic upgrade head
        ```
    - For downgrading migrations:
        ```bash
        poetry run alembic downgrade -1
        ```

## Packages

This project uses Poetry for dependency management. All required packages are listed in `pyproject.toml`.

## Static Typing

[**mypy**](https://mypy.readthedocs.io/en/stable/getting_started.html) is used for static typing. Ensure to use it in the project.

## Code Style

[Black](https://github.com/psf/black) is used to enforce a consistent code style. Run the following command:
```bash
poetry run black .
