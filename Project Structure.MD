# Project structure:
author-book-management-system/
│
├── main.py                 # Entry point for the app (e.g. FastAPI instance)
├── run.py                  # Script to launch the server (e.g. uvicorn runner)
│
├── api/
│   ├── config/             # Configuration settings
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── models/             # ORM models for authors, books, users
│   │   ├── __init__.py
│   │   ├── authors.py
│   │   ├── books.py
│   │   └── users.py
│   │
│   ├── routes/             # API route handlers
│   │   ├── __init__.py
│   │   ├── authors.py
│   │   ├── books.py
│   │   └── users.py
│   │
│   ├── utils/              # Helper functions and shared logic
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── email.py
│   │   ├── responses.py
│   │   ├── test_base.py
│   │   └── token.py
│   │
│   └── tests/              # All test files
│       ├── test_authors.py
│       └── test_users.py
│
└── __pycache__/            # Auto-generated compiled Python files



# Run the app:
run.py flask run

# Run unit test command:
python -m unittest discover api/tests

# Run unit test with coverage:

# 1. Install coverage:
pip install coverage

# 2. Run your tests with coverage:
coverage run -m unittest discover api/tests

# 3. Generate a coverage report:
coverage report

# 4. View a detailed HTML report:
coverage html
Then open htmlcov/index.html in your browser. You’ll see line-by-line coverage with color-coded highlights.

# 5. Optional: Erase old data:
coverage erase
