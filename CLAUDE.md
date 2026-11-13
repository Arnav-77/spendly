# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Windows, from the repo root:

- Create and activate the venv: `python -m venv venv` then `venv\Scripts\activate` (the `venv/` folder is already present in the repo)
- Install dependencies: `pip install -r requirements.txt`
- Run the dev server: `python app.py` (Flask debug mode on http://localhost:5001)
- Run tests: `pytest` (pytest and pytest-flask are in requirements.txt, but no test files exist yet)
- Run one test: `pytest path/to/test_file.py::test_name`

## Architecture

Spendly is a Flask expense tracker built as a course project. Most of the app is still stubs.

- `app.py` holds the whole Flask app: one `app` object and every route. Routes that render pages are implemented (`/`, `/register`, `/login`, `/terms`, `/privacy`). Routes for `/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit` and `/expenses/<id>/delete` return placeholder strings and are meant to be built in later steps.
- `database/db.py` is only a comment block. It is meant to provide `get_db()` (SQLite connection with row factory and foreign keys on), `init_db()` (CREATE TABLE IF NOT EXISTS) and `seed_db()` (sample data). The database file is `expense_tracker.db`, which is gitignored.
- `templates/base.html` is the shared layout: navbar, `{% block content %}`, footer (with links to `/terms` and `/privacy`), `main.js`, and a `{% block scripts %}` slot for page-specific JavaScript. Every page template extends it.
- `templates/login.html` and `templates/register.html` post to `/login` and `/register`, but those routes only accept GET, so a submit returns 405 until POST handlers are added.
- `static/css/style.css` defines the theme as CSS variables in `:root` (`--ink`, `--ink-muted`, and so on) and is the only stylesheet. Reuse those variables rather than hard-coding colours.
- `static/js/main.js` is an empty placeholder for shared JavaScript. Page-specific scripts go in the template's `scripts` block.

## Conventions

- Legal pages (`terms.html`, `privacy.html`) share the `legal-*` CSS classes. Reuse them for any new text-heavy page.
- Use `url_for()` for internal links, as the existing templates do.
