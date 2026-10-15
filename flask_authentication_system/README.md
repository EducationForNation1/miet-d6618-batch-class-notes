# Flask Complete Authentication System — Classes 1–15

This ZIP contains the complete project built through the 15-class course.

## Features

Registration, frontend/backend validation, password hashing, email verification, email/username login, sessions, Remember Me, protected routes, dashboard, profile, edit profile, change password, forgot/reset password, one-time reset tokens, admin role, role-based authorization, user management, search, pagination, block/unblock, role change, delete user, login history, CSRF protection, temporary lockout, security headers, and error pages.

## Run in VS Code

### 1. Create and activate virtual environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run
```bash
python app.py
```
Open `http://127.0.0.1:5000`.

The SQLite database is created automatically at `instance/auth.db`.

## Email verification and password-reset email

Edit `.env` and set:
```text
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
```
For Gmail SMTP, use an App Password rather than your normal account password.

If email is not configured, registration still creates the user but the account remains unverified. For classroom testing you can manually verify it:

```bash
python
```
```python
from app import app, db, User
with app.app_context():
    user = db.session.execute(
        db.select(User).filter_by(email="student@gmail.com")
    ).scalar_one_or_none()
    if user:
        user.is_verified = True
        db.session.commit()
```

## Create the first admin

Register and verify an account, then:
```bash
python
```
```python
from app import app, db, User
with app.app_context():
    user = db.session.execute(
        db.select(User).filter_by(email="admin@gmail.com")
    ).scalar_one_or_none()
    if user:
        user.role = "admin"
        user.is_active = True
        user.is_verified = True
        db.session.commit()
```
Log out and login again. Admin accounts are redirected to `/admin`.

## Production notes

Do not use the Flask development server publicly. Set `FLASK_ENV=production`, generate a new strong `SECRET_KEY`, configure HTTPS and `TRUSTED_HOSTS`, use a production database with backups, configure SMTP, and run through a production WSGI server such as `gunicorn app:app`.

## Course Mapping

1. Setup and first Flask app
2. SQLite + SQLAlchemy + User model
3. Registration UI + JavaScript validation
4. Registration backend + hashing
5. Login
6. Sessions + Remember Me + `login_required`
7. Dashboard + profile
8. Edit profile
9. Change password
10. Email verification
11. Forgot/reset password
12. Admin role + authorization
13. Admin user management + search + pagination
14. Login history + security activity
15. CSRF + lockout + headers + errors + deployment preparation
