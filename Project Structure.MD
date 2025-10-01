# Project structure:


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
