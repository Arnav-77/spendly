# Spec: Login and Logout

## Overview
Let a registered user sign in to Spendly and sign out again. The `/login` page already exists and shows a form, but submitting it returns 405 because the route only accepts GET. This step adds the POST handler that looks up the user by email, checks the password against the stored hash, and starts a session that remembers who is signed in. It also replaces the placeholder `/logout` route with a real one that ends the session. A session is how the app knows which user made each later request, so the profile page (step 4) and expense pages (steps 7 to 9) depend on this step.

## Depends on
- Step 1, Database Setup: the `users` table, `get_db()`, and `init_db()` must exist and run at startup.
- Step 2, Registration: there must be a user with a hashed password to sign in with. The seeded demo account (`demo@spendly.com` / `demo123`) also works for manual testing.

## Routes
- `GET /login`: show the sign-in form. Already exists. Public. No change in behaviour.
- `POST /login`: check the email and password. On success, start a session and redirect to `/profile`. On failure, re-render the form with an error. Public. New.
- `GET /logout`: clear the session and redirect to `/`. Public. Replaces the placeholder that returns "Logout coming in Step 3".

Behaviour of `POST /login`:
- Missing email or missing password: re-render `login.html` with an `error` message, keep the email the user typed, return HTTP 400.
- Email not found, or password does not match: re-render `login.html` with the same error message, "Invalid email or password.", keep the email, return HTTP 401. Do not reveal which of the two was wrong.
- Success: call `session.clear()`, store the user's id in `session["user_id"]`, and redirect (302) to `/profile`.

Behaviour of `GET /logout`:
- Call `session.clear()` and redirect (302) to `/`. Works whether or not anyone is signed in.

Input rules:
- `email`: trimmed and lowercased before lookup, the same as registration.
- `password`: not trimmed, the same as registration.

## Database changes
No schema changes. The `users` table already has `id`, `email`, and `password_hash`.

One existing helper changes. `get_user_by_email(email)` in `database/db.py` currently selects only `id`. Login needs `password_hash` and `name`, so the query becomes `SELECT id, name, email, password_hash FROM users WHERE email = ?`. Registration only checks whether the result is `None`, so it is not affected.

## Templates
- **Create:** none.
- **Modify:**
  - `templates/login.html`:
    - Change the form action from the hard-coded `/login` to `{{ url_for('login') }}`, following the project convention.
    - Fill the `email` input from a value passed by the route (`value="{{ email or '' }}"`). Never fill the password.
    - Keep the existing `{% if error %}` block.
  - `templates/base.html`:
    - In the navbar, show "Sign in" and "Get started" when no user is signed in, and a "Log out" link to `{{ url_for('logout') }}` when one is. The check is `session.get("user_id")`, so `session` must be available in templates (Flask provides it by default).

## Files to change
- `app.py`:
  - Import `session` from Flask and `check_password_hash` from `werkzeug.security`.
  - Set a secret key for signing the session cookie: `app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")`. Add `import os`. The fallback is for local development only. Anyone deploying must set `SECRET_KEY`.
  - Change `/login` to accept `methods=["GET", "POST"]` and add the POST logic above. Keep the GET behaviour.
  - Replace the `/logout` placeholder with the real handler above.
  - Leave `/profile`, `/expenses/add`, `/expenses/<id>/edit`, and `/expenses/<id>/delete` unchanged.
- `database/db.py`: widen the `SELECT` in `get_user_by_email` as described above.
- `templates/login.html`: see Templates above.
- `templates/base.html`: see Templates above.

## Files to create
- None.

## New dependencies
No new dependencies. `session` comes with Flask. `check_password_hash` comes with `werkzeug.security`, which is already installed.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterised queries only. No string formatting or f-strings inside SQL.
- Verify passwords with `werkzeug.security.check_password_hash`. Never compare plain text, and never store, log, or print the password.
- On a failed login, return the same message and status for "no such email" and "wrong password".
- Call `session.clear()` before storing `user_id`, so an old session cannot be reused after a new sign-in.
- Store only `user_id` in the session. Do not store the password, the hash, or the email in the session.
- Never put the secret key in the source code as a real value. Read it from the `SECRET_KEY` environment variable.
- Use CSS variables from `static/css/style.css`. Never hardcode hex values.
- All templates extend `base.html`.
- Use `url_for()` for internal links and form actions.
- Close database connections in a `finally` block, the same way `db.py` already does.
- Do not change the `/register` route or the `/profile` and expense placeholder routes.

## Definition of done
- [x] `GET /login` still returns the form with status 200.
- [x] Signing in with the demo account (`demo@spendly.com` / `demo123`) redirects to `/profile`, and the placeholder text "Profile page coming in Step 4" appears.
- [x] After signing in, the navbar shows "Log out" and no longer shows "Sign in" or "Get started".
- [x] Signing in with a wrong password shows "Invalid email or password." on the form, returns status 401, and does not set `user_id` in the session.
- [x] Signing in with an email that does not exist shows the same message and status as a wrong password.
- [x] Submitting the form with an empty email or empty password shows an error and returns status 400.
- [x] After a failed sign-in, the email field still contains what was typed. The password field is empty.
- [x] Emails differing only in letter case (for example `Demo@Spendly.com`) sign in to the same account.
- [x] Visiting `/logout` redirects to `/`, and the navbar goes back to showing "Sign in" and "Get started".
- [x] After logging out, visiting `/profile` does not show the signed-in state. (The profile page is still a placeholder until step 4. Check the session cookie instead: it no longer contains `user_id`.)
- [x] Logging in as one user, then logging in as another without logging out, leaves only the second user's id in the session.
- [x] Typing `<script>` into the email field and submitting shows it as plain text, not as running code.
- [x] The app starts with `python app.py` and no errors appear in the console.
- [x] Registration still works: `POST /register` with a new user creates the row and redirects to `/login`.
