# flask-taskflow

An enhanced Flask-based task management application featuring task prioritization, deadline tracking, dashboard analytics and user authentication.

---

## About this fork

This is my own fork of [23f2003608/Flask-learn-app](https://github.com/23f2003608/Flask-learn-app), a small beginner Flask project with signup, login and a notes page.

The fork turns that notes app into a task manager. Everything listed under **What I added** below is my own work on this fork. It is not a contribution to, and has not been merged into, the original project.

### What I added

- Replaced the notes model and pages with a `Task` model (title, description, priority, status, due date, owner)
- Task CRUD: create, edit and delete tasks from the web UI, with per-user ownership checks (users cannot see or change each other's tasks)
- Priority levels: Low, Medium, High
- Status tracking: Pending, In Progress, Completed
- Due dates, with an "Overdue" badge on open tasks past their deadline
- Input validation with flash messages on the forms
- Test suite (pytest) covering the task features and ownership rules
- Fixed a signup bug: a newly created account is now logged in (previously the code passed the wrong variable to `login_user`)
- Configurable `SECRET_KEY` through the `SECRET_KEY` environment variable

### Roadmap

Built in phases, so each one can be tested before the next starts:

1. **Done:** Task CRUD, priority levels, status tracking, due dates
2. **Next:** Search and filter by name, priority and status
3. **Then:** Dashboard with task statistics (Chart.js charts)
4. **Later:** Dark mode toggle

---

## Tech stack

- Python 3 with Flask 3 and Flask-Login
- Flask-SQLAlchemy with SQLite (`instance/database.db`)
- Jinja2 templates with Bootstrap 4
- pytest for tests

See `requirements.txt` for runtime dependencies and `requirements-dev.txt` for test dependencies.

---

## Project structure

- `main.py` — entrypoint that creates the app
- `website/__init__.py` — app factory, database setup, login manager
- `website/models.py` — `User` and `Task` models, priority and status choices
- `website/views.py` — task routes (list, create, edit, delete)
- `website/auth.py` — signup, login and logout routes
- `website/templates/` — `base.html`, `home.html` (task list), `task_form.html` (create and edit), `login.html`, `signup.html`
- `tests/` — pytest suite

---

## Setup

Requires Python 3.9 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Open http://127.0.0.1:5000, sign up, and start adding tasks. The SQLite database is created automatically in `instance/` on first run.

To set a real secret key, export `SECRET_KEY` before running:

```bash
export SECRET_KEY="a-long-random-string"
```

### Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

---

## Screenshots

_To be added once the UI is finished._

---

## Acknowledgements

Based on the beginner project [Flask-learn-app](https://github.com/23f2003608/Flask-learn-app). Flask documentation: https://flask.palletsprojects.com/
