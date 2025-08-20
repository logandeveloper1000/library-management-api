# Library API

A production-ready RESTful API for managing a library system. It includes user (member) registration and login with JWT authentication, books catalog with pagination and search, loans linking members to books, a simple store (items & orders), Swagger UI docs, caching and rate limiting, unit tests, and CI/CD to Render via GitHub Actions.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)
- [API Documentation (Swagger UI)](#api-documentation-swagger-ui)
- [Auth Flow](#auth-flow)
- [Endpoints Overview](#endpoints-overview)
- [Testing](#testing)
- [CI/CD (GitHub Actions → Render)](#cicd-github-actions--render)
- [Troubleshooting](#troubleshooting)
- [Notes & Security](#notes--security)
- [License](#license)

---

## Features

- **Members**: register, login (JWT), list, update, delete  
  - `POST /members/login` issues a bearer token.  
  - `POST /members/` is **rate limited** to `3 per hour`.  
  - `PUT /members/` and `DELETE /members/` are **protected** routes (JWT required).

- **Books**: create, list (optionally **paginated**), update, delete, search by title, and list by popularity (derived from loans).

- **Loans**: create a loan for a member and associate multiple books, edit a loan (add/remove books), list, delete.

- **Items & Orders**: simple store to sell items and create orders that produce a **receipt** with a computed total.

- **Swagger UI**: served from `/api/docs` using a static `swagger.yaml` (OpenAPI 2.0).

- **Caching**: integrated via `Flask-Caching` (sample usage in books route; easy to enable).

- **Rate Limiting**: global defaults (`200/day` and `50/hour`) and per-route example on member creation via `Flask-Limiter`.

- **Unit Tests**: example tests for the members flow with `unittest` and a SQLite test database.

- **CI/CD**: GitHub Actions with separate **build**, **test**, and **deploy** jobs; deploy to Render using `johnbeynon/render-deploy-action`.

---

## Architecture

```
app/
  __init__.py             # application factory and blueprint registration
  extensions.py           # Marshmallow, Limiter, Cache initialization
  models.py               # SQLAlchemy models (Member, Book, Loan, Item, Order, OrderItems)
  utils/
    util.py               # JWT helpers: encode_token + token_required decorator
  blueprints/
    members/
      __init__.py
      routes.py           # register/login, CRUD (update/delete are token-protected)
      schemas.py
    books/
      __init__.py
      routes.py           # CRUD, pagination, search, popularity
      schemas.py
    loans/
      __init__.py
      routes.py           # create/edit/list/delete loans
      schemas.py
    items/
      __init__.py
      routes.py           # CRUD
      schemas.py
    orders/
      __init__.py
      routes.py           # create order & receipt
      schemas.py
  static/
    swagger.yaml          # OpenAPI 2.0 spec for the UI

flask_app.py              # WSGI entrypoint
config.py                 # Development/Testing/Production configs
tests/
  test_members.py         # unit tests for members flow

.github/workflows/main.yaml  # CI/CD pipeline
```

---

## Tech Stack

- **Python 3.12**  
- **Flask**, **Flask-SQLAlchemy**, **SQLAlchemy 2.x Declarative**  
- **Marshmallow** / **Flask-Marshmallow** for schemas and validation  
- **PyJWT** for JSON Web Tokens  
- **Flask-Limiter** for rate limiting  
- **Flask-Caching** for response/data caching  
- **Swagger UI** (`flask-swagger-ui`) for API docs  
- **PostgreSQL / MySQL / SQLite** (configurable per environment)  
- **unittest** for testing  
- **GitHub Actions** for CI/CD, **Render** for hosting

---

## Quick Start

1. **Clone & create a virtual environment**
   ```bash
   git clone <your-repo-url> library-api
   cd library-api
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Create a `.env` (do NOT commit)** and set at least:
   ```ini
   SQLALCHEMY_DATABASE_URI=postgresql://<user>:<pass>@<host>/<db>
   SECRET_KEY=<a-long-random-string>
   ```

3. **Pick a config**  
   - For **local development**, use `DevelopmentConfig` and a local DB.  
   - For **tests**, `TestingConfig` uses SQLite.  
   - For **production**, use `ProductionConfig` with env vars.

   In `flask_app.py`, choose the config:
   ```python
   # flask_app.py
   from app import create_app
   app = create_app('DevelopmentConfig')  # switch to 'ProductionConfig' in prod
   ```

4. **Run the app**
   ```bash
   export FLASK_APP=flask_app.py
   flask run
   ```

   App will be available at `http://127.0.0.1:5000/`.

---

## Environment Variables

- `SQLALCHEMY_DATABASE_URI` — SQLAlchemy DSN for your environment (Postgres/MySQL/SQLite).  
- `SECRET_KEY` — used for JWT signing. **Generate a strong value and keep it secret.**

Optional (depending on your deployment):
- `RENDER_API_KEY`, `SERVICE_ID` — used by the GitHub Actions deploy step to Render.

---

## Running Locally

1. **Migrations/data**: this project calls `db.create_all()` in `flask_app.py`. For production-grade schemas, consider adding Alembic migrations later.  
2. **Swagger UI**: visit `http://127.0.0.1:5000/api/docs`.  
3. **Token usage**: copy the token from `/members/login` and pass `"Authorization: Bearer <token>"` on protected routes.

---

## API Documentation (Swagger UI)

- Path: **`/api/docs`**
- Spec: **`/static/swagger.yaml`**

> **Important:** Update the `host:` in `app/static/swagger.yaml` to your actual host (e.g., `localhost:5000` for local, or your Render domain). The YAML is set to HTTPS; ensure your deployment supports it.

---

## Auth Flow

1. **Register**
   ```http
   POST /members/
   Content-Type: application/json

   {
     "name": "John Doe",
     "email": "john@example.com",
     "DOB": "1990-01-01",
     "password": "secret123"
   }
   ```
   Returns `201` with the created member.

2. **Login**
   ```http
   POST /members/login
   Content-Type: application/json

   { "email": "john@example.com", "password": "secret123" }
   ```
   Returns `200` with `{ token, message, status }`.

3. **Use Token**
   ```http
   PUT /members/
   Authorization: Bearer <token>
   Content-Type: application/json

   { "name": "John Updated", "email": "john@example.com", "DOB": "1990-01-01", "password": "secret123" }
   ```

---

## Endpoints Overview

### Members
- `POST /members/` — register (**rate limited 3/hour**)
- `POST /members/login` — login & receive JWT
- `GET /members/` — list all members
- `PUT /members/` — update current member (**JWT required**, uses `token_required` to inject `member_id`)
- `DELETE /members/` — delete current member (**JWT required**)

### Books
- `POST /books/` — create a book
- `GET /books/?page=1&per_page=10` — list books (supports pagination; falls back to full list if params absent/invalid)
- `PUT /books/<book_id>` — update a book
- `DELETE /books/<book_id>` — delete a book
- `GET /books/search?title=foo` — search by title (SQL LIKE)
- `GET /books/popular` — list books sorted by number of associated loans

### Loans
- `POST /loans/` — create a loan for a `member_id` with `book_ids[]`
- `GET /loans/` — list loans (includes nested books & member)
- `PUT /loans/<loan_id>` — edit loan (add/remove book IDs)
- `DELETE /loans/<loan_id>` — delete a loan

### Items & Orders
- `POST /items/` | `GET /items/` | `PUT /items/<id>` | `DELETE /items/<id>`  
- `POST /orders/` — create order with `{ member_id, item_quant: [{ item_id, item_quant }] }` and receive a `receipt` (total and order detail).

---

## Testing

Run the unit tests (uses SQLite per `TestingConfig`):
```bash
python -m unittest discover -s tests -p 'test_*.py'
```

The sample `tests/test_members.py` covers: create member, invalid creation, login, invalid login, list members, delete with JWT, etc.

---

## CI/CD (GitHub Actions → Render)

Workflow: `.github/workflows/main.yaml`

- **build**: checkout → set up Python 3.12 → create venv → install deps → print debugging info
- **test**: depends on `build`; repeats setup → runs unit tests
- **deploy**: depends on `test`; deploys to **Render** using `johnbeynon/render-deploy-action@v0.0.8`

**Secrets required in GitHub repo settings → Actions secrets and variables → Secrets:**

- `RENDER_API_KEY` — Render API token
- `SERVICE_ID` — Render service ID for your web service

> The Swagger spec (`static/swagger.yaml`) has `host:` set. Make sure it matches your Render URL in production.

---

## Troubleshooting

- **Swagger host mismatch**: Set `host:` in `static/swagger.yaml` to your current host (e.g., `localhost:5000` for local, `your-service.onrender.com` in prod).

- **CI “Print debugging information” step**: ensure the command uses `ls -l` (with a space and hyphen).  
  In your YAML, replace `ls-l` with `ls -l` and remove any stray characters at the end of that step.

- **JWT “token expired”**: tokens currently expire in 1 hour (`util.py`). Log in again to refresh.

- **Database drivers**: verify that your `SQLALCHEMY_DATABASE_URI` matches the driver installed (e.g., `postgresql+psycopg2://...` if you use psycopg2, or `mysql+mysqlconnector://...` if using MySQL Connector/Python).

- **Caching**: The example `@cache.cached(timeout=60)` on `GET /books/` is commented out. Uncomment to enable simple caching for that route.

---

## Notes & Security

- **Never commit `.env`** or real credentials. Rotate any secrets that were committed previously.  
- Use unique, strong `SECRET_KEY` values per environment.  
- Consider adding **Alembic** for migrations and **proper password hashing** for members (e.g., `werkzeug.security` or `bcrypt`) before production use.

---

## License

This project is provided as-is for educational and portfolio use. Add a `LICENSE` file to specify your preferred license (MIT, Apache-2.0, etc.).
