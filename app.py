import os
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)
# Signs the session cookie. Set SECRET_KEY in any real deployment; the fallback is for local development only.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


DUPLICATE_EMAIL_MESSAGE = "An account with this email already exists."


def _is_valid_email(email):
    """Basic check only: one @, a non-empty local part, a dot in the domain, no spaces."""
    if " " in email or email.count("@") != 1:
        return False
    local, domain = email.split("@")
    return bool(local) and "." in domain and not domain.startswith(".") and not domain.endswith(".")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    def show_error(message):
        # The password is never sent back to the form.
        return render_template("register.html", error=message, name=name, email=email), 400

    if not name:
        return show_error("Please enter your name.")
    if not _is_valid_email(email):
        return show_error("Please enter a valid email address.")
    if len(password) < 8:
        return show_error("Password must be at least 8 characters.")
    if get_user_by_email(email) is not None:
        return show_error(DUPLICATE_EMAIL_MESSAGE)

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        # Two requests with the same email can both pass the check above.
        # The UNIQUE constraint catches the second one.
        return show_error(DUPLICATE_EMAIL_MESSAGE)

    return redirect(url_for("login"))


INVALID_LOGIN_MESSAGE = "Invalid email or password."


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    def show_error(message, status):
        # The password is never sent back to the form.
        return render_template("login.html", error=message, email=email), status

    if not email or not password:
        return show_error("Please enter your email and password.", 400)

    user = get_user_by_email(email)
    # Same message and status whether the email is unknown or the password is wrong.
    if user is None or not check_password_hash(user["password_hash"], password):
        return show_error(INVALID_LOGIN_MESSAGE, 401)

    # Clear first so an older session cannot survive a new sign-in.
    session.clear()
    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Step 4 uses hardcoded data only. Step 5 replaces these with database queries.
    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "member_since": "1 October 2026",
        "initials": "DU",
    }
    stats = {
        "total_spent": 3649.50,
        "transaction_count": 8,
        "top_category": "Shopping",
    }
    transactions = [
        {"date": "02 Nov 2026", "description": "Groceries", "category": "Food", "amount": 450.00},
        {"date": "04 Nov 2026", "description": "Metro card top-up", "category": "Transport", "amount": 120.50},
        {"date": "06 Nov 2026", "description": "Mobile recharge", "category": "Bills", "amount": 899.00},
        {"date": "08 Nov 2026", "description": "Pharmacy", "category": "Health", "amount": 350.00},
        {"date": "10 Nov 2026", "description": "Movie tickets", "category": "Entertainment", "amount": 250.00},
        {"date": "12 Nov 2026", "description": "Winter jacket", "category": "Shopping", "amount": 1200.00},
        {"date": "13 Nov 2026", "description": "Stationery", "category": "Other", "amount": 80.00},
        {"date": "14 Nov 2026", "description": "Dinner out", "category": "Food", "amount": 300.00},
    ]
    # percent is the share of total spent, rounded to the nearest 5 for the bar width class.
    # Other is 2.2%, which rounds to 0; it is shown as 5 so the bar is still visible.
    categories = [
        {"name": "Shopping", "total": 1200.00, "percent": 35},
        {"name": "Bills", "total": 899.00, "percent": 25},
        {"name": "Food", "total": 750.00, "percent": 20},
        {"name": "Health", "total": 350.00, "percent": 10},
        {"name": "Entertainment", "total": 250.00, "percent": 5},
        {"name": "Transport", "total": 120.50, "percent": 5},
        {"name": "Other", "total": 80.00, "percent": 5},
    ]

    return render_template(
        "profile.html",
        user=user,
        user_name=user["name"],
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
