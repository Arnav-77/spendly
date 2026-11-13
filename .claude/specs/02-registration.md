# Spec: Registration

## Overview
Let a new visitor create a Spendly account. The `/register` page already exists and shows a form, but submitting it does nothing yet. This step adds the POST handler that validates the form, stores the new user in the `users` table with a hashed password, and sends them on to the sign-in page. Registration comes before login (step 3) because there must be users before anyone can sign in. The database layer from step 1 provides the `users` table and `get_db()`.

## Depends on
- Step 1, Database Setup: the `users` table, `get_db()`, and `init_db()` must exist and run at startup.

## Routes
- `GET /register`: show the registration form. Already exists. Public. No change in behaviour.
- `POST /register`: validate the form, create the user, redirect to `/login`. Public. New.

Behaviour of `POST /register`:
- Missing name, missing email, or password shorter than 8 characters: re-render `register.html` with an `error` message, keep the name and email the user typed, and return HTTP 400.
- Email already in use: re-render with an error such as "An account with this email already exists." Return HTTP 400. Keep the name and email, never the password.
- Success: insert the user and redirect (302) to `/login`.

Validation rules:
- `name`: required after trimming whitespace.
- `email`: required after trimming, lowercased before storage, must contain `@` and a dot after it. Full email validation is not needed.
- `password`: at least 8 characters. Not trimmed.

## Database changes
No database changes. The `users` table in `database/db.py` already has `name`, `email` (UNIQUE, NOT NULL), `password_hash` (NOT NULL), and `created_at` (default `datetime('now')`). The duplicate-email check is done with a query first, so the user gets a friendly message. The UNIQUE constraint is the backstop if two requests race.

## Templates
- **Create:** none.
- **Modify:**
  - `templates/register.html`:
    - Fill the `name` and `email` inputs from values passed by the route (`value="{{ name or '' }}"`, same for email). Never fill the password.
    - Change the form action from the hard-coded `/register` to `{{ url_for('register') }}`, to follow the project convention.
    - Keep the existing `{% if error %}` block, which already displays errors.

## Files to change
- `app.py`: add `POST` to the `/register` route, read the form, call a helper, and redirect or re-render. Keep the existing `GET` behaviour.
- `database/db.py`: add a function `create_user(name, email, password)` that hashes the password and inserts the row. Also add `get_user_by_email(email)` for the duplicate check. Both use `get_db()` and parameterised queries.
- `templates/register.html`: see Templates above.

## Files to create
- None.

## New dependencies
No new dependencies. `werkzeug.security` is already installed with Flask.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterised queries only. No string formatting or f-strings inside SQL.
- Passwords hashed with `werkzeug.security.generate_password_hash`. Plain-text passwords must never be stored, logged, or put in a template.
- Use CSS variables from `static/css/style.css`. Never hardcode hex values.
- All templates extend `base.html`.
- Use `url_for()` for internal links and form actions.
- Do not change the placeholder routes (`/logout`, `/profile`, expense routes).
- Close database connections in a `finally` block, the same way `db.py` already does.
- Do not auto-login the user after registering. Login is step 3.

## Definition of done
- [ ] `GET /register` still returns the form with status 200.
- [ ] Submitting the form with valid data creates one new row in `users`, and the browser lands on `/login`.
- [ ] The stored `password_hash` is not equal to the typed password, and `check_password_hash` accepts the typed password.
- [ ] Submitting with an empty name shows an error on the form and creates no row.
- [ ] Submitting with an empty email shows an error on the form and creates no row.
- [ ] Submitting a password with fewer than 8 characters shows an error and creates no row.
- [ ] Submitting an email that already exists shows "An account with this email already exists." and creates no row.
- [ ] After a validation error, the name and email fields still contain what was typed. The password field is empty.
- [ ] Emails differing only in letter case (for example `Nitish@Example.com` and `nitish@example.com`) are treated as the same account.
- [ ] Typing `<script>` into the name field and submitting shows it as plain text, not as running code.
- [ ] The app starts with `python app.py` and no errors appear in the console.
- [ ] The placeholder routes still return their placeholder text.
