from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
from datetime import timedelta

app = Flask(__name__)

# Required for Flask sessions and flash messages.
# In production, load this value from an environment variable.
app.secret_key = "change-this-secret-key-in-production"

# Session will expire after 30 minutes of inactivity.
app.permanent_session_lifetime = timedelta(minutes=30)


@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# COOKIE EXAMPLES
# -----------------------------

@app.route("/set-cookie")
def set_cookie():
    response = make_response(render_template(
        "message.html",
        title="Cookie Created",
        message="Cookie 'username=Deepak' has been created for 1 hour."
    ))

    response.set_cookie(
        "username",
        "Deepak",
        max_age=60 * 60,
        httponly=True,
        samesite="Lax"
    )
    return response


@app.route("/get-cookie")
def get_cookie():
    username = request.cookies.get("username")

    if username:
        message = f"Cookie value found: {username}"
    else:
        message = "Cookie not found. Please set the cookie first."

    return render_template(
        "message.html",
        title="Read Cookie",
        message=message
    )


@app.route("/delete-cookie")
def delete_cookie():
    response = make_response(render_template(
        "message.html",
        title="Cookie Deleted",
        message="The username cookie has been deleted."
    ))
    response.delete_cookie("username")
    return response


# -----------------------------
# SESSION / LOGIN EXAMPLES
# -----------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, go directly to dashboard.
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Demo credentials only.
        # Real applications should check a database and hashed password.
        if email == "admin@gmail.com" and password == "12345":
            session.permanent = True
            session["user_id"] = 101
            session["email"] = email
            session["username"] = "Deepak"

            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        email=session.get("email"),
        user_id=session.get("user_id")
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/session-info")
def session_info():
    if "user_id" not in session:
        return render_template(
            "message.html",
            title="Session Information",
            message="No active login session. Please login first."
        )

    message = (
        f"User ID: {session.get('user_id')} | "
        f"Username: {session.get('username')} | "
        f"Email: {session.get('email')}"
    )

    return render_template(
        "message.html",
        title="Session Information",
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)
