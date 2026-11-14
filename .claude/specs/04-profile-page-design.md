# Spec: Profile Page Design

## Overview
This feature replaces the `/profile` stub with a complete, visually designed profile page that shows hardcoded data. It is the design pass for Step 4 of the Spendly roadmap: the user info card, summary stats, transaction history table and category breakdown are laid out and styled using the existing CSS variables, with no database queries. Designing the page with static data first lets the layout be reviewed in isolation, and it leaves the templates ready for Step 5, which swaps the hardcoded dicts for real queries without changing the markup.

## Depends on
- Step 1: Database setup (schema exists, so Step 5 can query the same tables later)
- Step 2: Registration (accounts can be created)
- Step 3: Login and Logout (session holds `user_id`; `/profile` is a protected route)

## Routes
- `GET /profile` — render the profile page with hardcoded data — logged-in only (redirect to `/login` if `session.get("user_id")` is missing)

## Database changes
No database changes. The existing `users` and `expenses` tables are not read in this step.

## Templates
- **Create:** `templates/profile.html`. Extends `base.html`. Contains four sections, in this order:
  1. **User info card** — initials avatar, full name, email, "Member since" date.
  2. **Summary stats row** — three tiles: total spent, number of transactions, top category.
  3. **Transaction history table** — columns: date, description, category badge, amount. At least eight rows, with the amount right-aligned.
  4. **Category breakdown** — one row per category with name, total and a progress bar whose width comes from a CSS class (for example `bar-35`), not an inline style.
- **Modify:** `templates/base.html` — restore the signed-in name in the navbar (`{% if user_name %}<span class="nav-user">...</span>{% endif %}`), so the navbar shows the logged-in state. This matches the earlier commit `6f4a128`.
- **Modify:** `static/css/style.css` — add a `profile-*` block (card, stat tile, badge, bar) that reuses the existing variables. Add no new colours.

## Files to change
- `app.py` — replace the `/profile` stub with a view that:
  - Redirects to `url_for("login")` when `session.get("user_id")` is missing.
  - Builds `user`, `user_name`, `stats`, `transactions` and `categories` as hardcoded Python dicts and lists, then calls `render_template("profile.html", ...)`.
- `templates/base.html` — restore the navbar name (see Templates).
- `static/css/style.css` — add profile layout and component classes.

## Files to create
- `templates/profile.html`
- `.claude/specs/04-profile-page-design.md` (this file)

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs. Any future database call uses raw sqlite3 through `get_db()`.
- Parameterised queries only. Never build SQL with string formatting. (This step has no queries.)
- Passwords hashed with werkzeug. No changes to auth in this step.
- Use CSS variables. Never hardcode hex values in `profile.html`, `app.py` or new CSS rules.
- All templates extend `base.html`.
- No inline styles in templates. Category bar widths and badge colours come from CSS classes.
- All data passed to the template is hardcoded in `app.py`. No database reads.
- Reuse the existing `legal-*` or card patterns from `style.css` where they fit. Do not duplicate them.
- Use `url_for()` for every internal link.
- The layout must work at phone width (about 360 px): the stats row stacks to one column, and the transaction table scrolls horizontally inside its own wrapper, not the whole page.

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`.
- [ ] Visiting `/profile` while logged in returns HTTP 200.
- [ ] The info card shows the name "Demo User", the email "demo@spendly.com", initials and a "Member since" date.
- [ ] The stats row shows three values: total spent, transaction count and top category.
- [ ] The transaction table shows at least eight rows, each with date, description, category badge and amount.
- [ ] The category breakdown shows at least three categories, each with a total and a bar.
- [ ] The navbar shows the signed-in name and a "Log out" link.
- [ ] `grep -n "#[0-9a-fA-F]\{3,6\}" templates/profile.html` returns nothing.
- [ ] `grep -n "style=" templates/profile.html` returns nothing.
- [ ] At a 360 px viewport the page has no horizontal scroll on the body. Only the table wrapper scrolls.
- [ ] Every internal link on the page resolves (checked by clicking through).
