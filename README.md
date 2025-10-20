# String Analyzer

Repository: https://github.com/Rita-mary/hng-stage1

Small Django + DRF project that analyzes strings (length, palindrome, word count, character frequency) and exposes endpoints to create, retrieve, list, and filter analyzed strings. It also includes a natural-language filtering endpoint.

## Quick setup (Windows)

1. Clone the repo:

```powershell
git clone https://github.com/Rita-mary/hng-stage1
cd HNG-STAGE1
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# or for cmd.exe
.\.venv\Scripts\activate.bat
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run migrations and start server:

```powershell
python manage.py migrate
python manage.py runserver
```

5. Open http://127.0.0.1:8000/ in your browser. Use the API routes under `/strings/` and `/strings/filter-by-natural-language`.

## Running tests

Run the full test suite with:

```powershell
python manage.py test --verbosity=2
```

## Endpoints
- POST /strings/ — create and analyze a string
- GET /strings/<value>/ — retrieve an analyzed string
- GET /strings — list analyzed strings with query filters (is_palindrome, min_length, max_length, contains_character, word_count)
- GET /strings/filter-by-natural-language?query=... — natural language filtering endpoint

Example NL query: `all single word palindromic strings` → parsed to `word_count=1` and `is_palindrome=true`.

## Dependencies
See `requirements.txt` for the exact pinned dependencies. Key packages:

- Django
- djangorestframework
- drf-spectacular (optional, for OpenAPI schema)

Install with `pip install -r requirements.txt`.

## Environment variables
- `DJANGO_SETTINGS_MODULE` — default is `string_analyzer.settings` (not required for local run with `manage.py`)
- `SECRET_KEY` — the Django secret (for production only; dev uses default in settings)
- Database: the project uses SQLite by default (`db.sqlite3`). No additional env vars required for local development.

If you deploy to production, ensure you set `SECRET_KEY`, `DEBUG=0`, and configure a production database and allowed hosts.



