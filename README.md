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
    Update the database credentials in the `src/settings.py` before running the service.

6. **Database Migration**:
    - For upgrading migrations:
        ```bash
        poetry run alembic upgrade head
        ```
    - For downgrading migrations:
        ```bash
        poetry run alembic downgrade -1
        ```
7.  **Run the project**:
    - ```python .\src\ ```
