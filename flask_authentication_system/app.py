import os
import re
import secrets
import hashlib
from datetime import datetime, timedelta
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFError, CSRFProtect
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
app = Flask(__name__)

secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError("SECRET_KEY is not configured. Copy .env.example to .env and set SECRET_KEY.")

app.config["SECRET_KEY"] = secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///auth.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

IS_PRODUCTION = os.environ.get("FLASK_ENV", "development").lower() == "production"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
)

trusted_hosts = os.environ.get("TRUSTED_HOSTS", "").strip()
if trusted_hosts:
    app.config["TRUSTED_HOSTS"] = [x.strip() for x in trusted_hosts.split(",") if x.strip()]

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", "587"))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL", "false").lower() == "true"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME") or None
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD") or None
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME") or None

db = SQLAlchemy(app)
mail = Mail(app)
csrf = CSRFProtect(app)
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    identifier = db.Column(db.String(120), nullable=True)
    success = db.Column(db.Boolean, nullable=False, default=False, index=True)
    failure_reason = db.Column(db.String(50), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    logout_time = db.Column(db.DateTime, nullable=True)
    user = db.relationship("User", backref="login_history")

def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            session.clear(); flash("Please login first.", "error"); return redirect(url_for("login"))
        if not user.is_active:
            session.clear(); flash("Your account is disabled.", "error"); return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            session.clear(); flash("Please login first.", "error"); return redirect(url_for("login"))
        if not user.is_active:
            session.clear(); flash("Your account is disabled.", "error"); return redirect(url_for("login"))
        if user.role != "admin":
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

def generate_verification_token(user):
    return serializer.dumps({"user_id": user.id, "email": user.email}, salt="email-verification")

def ensure_mail():
    if not app.config.get("MAIL_USERNAME") or not app.config.get("MAIL_PASSWORD"):
        raise RuntimeError("Email is not configured.")

def send_verification_email(user):
    ensure_mail()
    token = generate_verification_token(user)
    verification_url = url_for("verify_email", token=token, _external=True)
    msg = Message("Verify Your Email", recipients=[user.email])
    msg.body = f"Hello {user.full_name},\n\nVerify your email:\n{verification_url}\n\nThis link expires in 30 minutes."
    msg.html = render_template("emails/verify_email.html", user=user, verification_url=verification_url)
    mail.send(msg)

def invalidate_reset_tokens(user_id):
    tokens = db.session.execute(db.select(PasswordResetToken).where(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.used_at.is_(None)
    )).scalars().all()
    now = datetime.utcnow()
    for token in tokens:
        token.used_at = now
    db.session.commit()

def create_reset_token(user):
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    db.session.add(PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    ))
    db.session.commit()
    return raw

def send_reset_email(user, raw_token):
    ensure_mail()
    reset_url = url_for("reset_password", token=raw_token, _external=True)
    msg = Message("Reset Your Password", recipients=[user.email])
    msg.body = f"Hello {user.full_name},\n\nReset your password:\n{reset_url}\n\nThis link expires in 30 minutes."
    msg.html = render_template("emails/reset_password.html", user=user, reset_url=reset_url)
    mail.send(msg)

def record_login(user=None, identifier="", success=False, reason=None):
    row = LoginHistory(
        user_id=user.id if user else None,
        identifier=(identifier or "")[:120],
        success=success,
        failure_reason=reason,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent", "")[:255],
    )
    db.session.add(row); db.session.commit(); return row

def account_locked_until(user):
    now = datetime.utcnow()
    start = now - timedelta(minutes=LOCKOUT_MINUTES)
    last_success = db.session.execute(
        db.select(LoginHistory).where(
            LoginHistory.user_id == user.id,
            LoginHistory.success.is_(True)
        ).order_by(LoginHistory.login_time.desc()).limit(1)
    ).scalar_one_or_none()
    if last_success and last_success.login_time > start:
        start = last_success.login_time
    failures = db.session.execute(
        db.select(LoginHistory).where(
            LoginHistory.user_id == user.id,
            LoginHistory.success.is_(False),
            LoginHistory.failure_reason == "Invalid Password",
            LoginHistory.login_time >= start
        ).order_by(LoginHistory.login_time.desc())
    ).scalars().all()
    if len(failures) < MAX_FAILED_ATTEMPTS:
        return None
    until = failures[0].login_time + timedelta(minutes=LOCKOUT_MINUTES)
    return until if now < until else None

@app.route("/")
def home():
    return render_template("index.html", user=current_user())

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        terms = request.form.get("terms")
        errors = []
        if len(full_name) < 3 or not full_name.replace(" ", "").isalpha(): errors.append("Enter a valid full name.")
        if not re.match(r"^[A-Za-z0-9_]{4,20}$", username): errors.append("Username must be 4-20 letters, numbers or underscore.")
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email): errors.append("Enter a valid email address.")
        if not phone.isdigit() or len(phone) != 10: errors.append("Phone number must contain exactly 10 digits.")
        pw = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(pw, password): errors.append("Password must contain 8+ characters, uppercase, lowercase, number and special character.")
        if password != confirm: errors.append("Passwords do not match.")
        if terms != "accepted": errors.append("Please accept the Terms & Conditions.")
        if db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none(): errors.append("Username already exists.")
        if db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none(): errors.append("Email already registered.")
        if errors:
            for e in errors: flash(e, "error")
            return redirect(url_for("register"))
        user = User(full_name=full_name, username=username, email=email, phone=phone, password=generate_password_hash(password), role="user")
        try:
            db.session.add(user); db.session.commit()
        except IntegrityError:
            db.session.rollback(); flash("Username or email already exists.", "error"); return redirect(url_for("register"))
        try:
            send_verification_email(user); flash("Account created. Please check your email to verify your account.", "success")
        except Exception:
            flash("Account created, but verification email could not be sent. Configure email and use Resend Verification.", "error")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/verify-email/<token>")
def verify_email(token):
    try:
        data = serializer.loads(token, salt="email-verification", max_age=1800)
        user = db.session.get(User, data.get("user_id"))
        if not user or user.email != data.get("email"):
            flash("This verification link is invalid or no longer valid.", "error"); return redirect(url_for("login"))
        if user.is_verified:
            flash("Your email is already verified.", "success"); return redirect(url_for("login"))
        user.is_verified = True; db.session.commit(); flash("Email verified successfully. You can now login.", "success")
        return redirect(url_for("login"))
    except SignatureExpired:
        flash("Verification link has expired. Please request a new verification email.", "error"); return redirect(url_for("resend_verification"))
    except BadSignature:
        flash("Invalid verification link.", "error"); return redirect(url_for("login"))

@app.route("/resend-verification", methods=["GET", "POST"])
def resend_verification():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none() if email else None
        if user and not user.is_verified:
            try: send_verification_email(user)
            except Exception: pass
        flash("If an unverified account exists for this email, a verification link has been sent.", "success")
        return redirect(url_for("resend_verification"))
    return render_template("resend_verification.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    user = current_user()
    if user and user.is_active:
        return redirect(url_for("admin_dashboard" if user.role == "admin" else "dashboard"))
    if user: session.clear()
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        if not identifier or not password:
            flash("Email/username and password are required.", "error"); return redirect(url_for("login"))
        user = db.session.execute(db.select(User).filter_by(email=identifier)).scalar_one_or_none()
        if not user: user = db.session.execute(db.select(User).filter_by(username=identifier)).scalar_one_or_none()
        if not user:
            record_login(None, identifier, False, "Invalid Credentials"); flash("Invalid email/username or password.", "error"); return redirect(url_for("login"))
        if not user.is_active:
            record_login(user, identifier, False, "Account Disabled"); flash("Your account is currently disabled.", "error"); return redirect(url_for("login"))
        if account_locked_until(user):
            record_login(user, identifier, False, "Temporary Lockout"); flash("Too many failed login attempts. Please try again later.", "error"); return redirect(url_for("login"))
        if not check_password_hash(user.password, password):
            record_login(user, identifier, False, "Invalid Password")
            flash("Too many failed login attempts. Please try again later." if account_locked_until(user) else "Invalid email/username or password.", "error")
            return redirect(url_for("login"))
        if not user.is_verified:
            record_login(user, identifier, False, "Email Not Verified"); flash("Please verify your email before logging in.", "error"); return redirect(url_for("login"))
        history = record_login(user, identifier, True, None)
        session.clear(); session["user_id"] = user.id; session["login_history_id"] = history.id; session.permanent = remember
        flash("Login successful.", "success")
        return redirect(url_for("admin_dashboard" if user.role == "admin" else "dashboard"))
    return render_template("login.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none() if email else None
        if user and user.is_active:
            try:
                invalidate_reset_tokens(user.id); raw = create_reset_token(user); send_reset_email(user, raw)
            except Exception: pass
        flash("If an account exists for this email, a password reset link has been sent.", "success")
        return redirect(url_for("forgot_password"))
    return render_template("forgot_password.html")

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    rec = db.session.execute(db.select(PasswordResetToken).filter_by(token_hash=token_hash)).scalar_one_or_none()
    if not rec: flash("Invalid password reset link.", "error"); return redirect(url_for("forgot_password"))
    if rec.used_at: flash("This password reset link has already been used.", "error"); return redirect(url_for("forgot_password"))
    if rec.expires_at < datetime.utcnow(): flash("Password reset link has expired.", "error"); return redirect(url_for("forgot_password"))
    user = db.session.get(User, rec.user_id)
    if not user or not user.is_active: flash("This password reset link is no longer valid.", "error"); return redirect(url_for("forgot_password"))
    if request.method == "POST":
        new = request.form.get("new_password", ""); confirm = request.form.get("confirm_password", "")
        pw = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(pw, new): flash("Password must contain 8+ characters, uppercase, lowercase, number and special character.", "error"); return redirect(url_for("reset_password", token=token))
        if new != confirm: flash("Passwords do not match.", "error"); return redirect(url_for("reset_password", token=token))
        if check_password_hash(user.password, new): flash("New password must be different from your current password.", "error"); return redirect(url_for("reset_password", token=token))
        user.password = generate_password_hash(new); now = datetime.utcnow(); rec.used_at = now
        others = db.session.execute(db.select(PasswordResetToken).where(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None))).scalars().all()
        for item in others: item.used_at = now
        db.session.commit(); session.clear(); flash("Password reset successfully. Please login with your new password.", "success"); return redirect(url_for("login"))
    return render_template("reset_password.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    logs = db.session.execute(db.select(LoginHistory).where(LoginHistory.user_id == user.id, LoginHistory.success.is_(True)).order_by(LoginHistory.login_time.desc()).limit(2)).scalars().all()
    return render_template("dashboard.html", user=user, previous_login=(logs[1] if len(logs) > 1 else None))

@app.route("/profile")
@login_required
def profile(): return render_template("profile.html", user=current_user())

@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = current_user()
    if request.method == "POST":
        name = request.form.get("full_name", "").strip(); username = request.form.get("username", "").strip().lower(); email = request.form.get("email", "").strip().lower(); phone = request.form.get("phone", "").strip(); errors=[]
        if len(name) < 3 or not name.replace(" ", "").isalpha(): errors.append("Enter a valid full name.")
        if not re.match(r"^[A-Za-z0-9_]{4,20}$", username): errors.append("Username must contain 4-20 letters, numbers or underscore.")
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email): errors.append("Enter a valid email address.")
        if not phone.isdigit() or len(phone) != 10: errors.append("Phone number must contain exactly 10 digits.")
        u = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none(); e = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if u and u.id != user.id: errors.append("Username already exists.")
        if e and e.id != user.id: errors.append("Email already registered.")
        if errors:
            for msg in errors: flash(msg, "error")
            return redirect(url_for("edit_profile"))
        email_changed = user.email != email; user.full_name=name; user.username=username; user.email=email; user.phone=phone
        if email_changed: user.is_verified=False
        db.session.commit()
        if email_changed:
            try: send_verification_email(user); flash("Profile updated. Please verify your new email address.", "success")
            except Exception: flash("Profile updated, but verification email could not be sent. Use Resend Verification.", "error")
        else: flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))
    return render_template("edit_profile.html", user=user)

@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    user = current_user()
    if request.method == "POST":
        current = request.form.get("current_password", ""); new = request.form.get("new_password", ""); confirm = request.form.get("confirm_password", "")
        pw = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not check_password_hash(user.password, current): flash("Current password is incorrect.", "error"); return redirect(url_for("change_password"))
        if not re.match(pw, new): flash("New password must contain 8+ characters, uppercase, lowercase, number and special character.", "error"); return redirect(url_for("change_password"))
        if new != confirm: flash("New passwords do not match.", "error"); return redirect(url_for("change_password"))
        if check_password_hash(user.password, new): flash("New password must be different from current password.", "error"); return redirect(url_for("change_password"))
        user.password=generate_password_hash(new); db.session.commit(); session.clear(); flash("Password changed successfully. Please login again.", "success"); return redirect(url_for("login"))
    return render_template("change_password.html", user=user)

@app.route("/security-activity")
@login_required
def security_activity():
    user=current_user(); page=request.args.get("page",1,type=int)
    stmt=db.select(LoginHistory).where(LoginHistory.user_id==user.id).order_by(LoginHistory.login_time.desc())
    pagination=db.paginate(stmt,page=page,per_page=10,error_out=False)
    return render_template("security_activity.html", user=user, records=pagination.items, pagination=pagination)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    user_id=session.get("user_id"); hid=session.get("login_history_id")
    if hid:
        row=db.session.get(LoginHistory,hid)
        if row and row.user_id==user_id and row.success and row.logout_time is None:
            row.logout_time=datetime.utcnow(); db.session.commit()
    session.clear(); flash("You have been logged out successfully.", "success"); return redirect(url_for("login"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    admin=current_user()
    count=lambda cond=None: db.session.scalar(db.select(db.func.count()).select_from(User).where(cond) if cond is not None else db.select(db.func.count()).select_from(User)) or 0
    return render_template("admin/dashboard.html", admin=admin, total_users=count(), active_users=count(User.is_active.is_(True)), blocked_users=count(User.is_active.is_(False)), verified_users=count(User.is_verified.is_(True)), unverified_users=count(User.is_verified.is_(False)), admin_users=count(User.role=="admin"))

@app.route("/admin/users")
@admin_required
def admin_users():
    page=request.args.get("page",1,type=int); search=request.args.get("search","").strip(); stmt=db.select(User).order_by(User.created_at.desc())
    if search:
        term=f"%{search}%"; stmt=stmt.where(or_(User.full_name.ilike(term),User.username.ilike(term),User.email.ilike(term)))
    pagination=db.paginate(stmt,page=page,per_page=10,error_out=False)
    return render_template("admin/users.html", users=pagination.items, pagination=pagination, search=search)

@app.route("/admin/users/<int:user_id>")
@admin_required
def admin_user_details(user_id):
    user=db.session.get(User,user_id)
    if not user: flash("User not found.","error"); return redirect(url_for("admin_users"))
    return render_template("admin/user_details.html", user=user)

@app.route("/admin/users/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def admin_toggle_user_status(user_id):
    user=db.session.get(User,user_id)
    if not user: flash("User not found.","error"); return redirect(url_for("admin_users"))
    if user.id==session["user_id"]: flash("You cannot block your own admin account.","error"); return redirect(url_for("admin_user_details",user_id=user.id))
    user.is_active=not user.is_active; db.session.commit(); flash("User unblocked successfully." if user.is_active else "User blocked successfully.","success"); return redirect(url_for("admin_user_details",user_id=user.id))

@app.route("/admin/users/<int:user_id>/role", methods=["POST"])
@admin_required
def admin_change_role(user_id):
    user=db.session.get(User,user_id)
    if not user: flash("User not found.","error"); return redirect(url_for("admin_users"))
    role=request.form.get("role","").strip().lower()
    if role not in {"user","admin"}: flash("Invalid role.","error"); return redirect(url_for("admin_user_details",user_id=user.id))
    if user.id==session["user_id"]: flash("You cannot change your own admin role.","error"); return redirect(url_for("admin_user_details",user_id=user.id))
    if user.role=="admin" and role!="admin":
        admins=db.session.scalar(db.select(db.func.count()).select_from(User).where(User.role=="admin")) or 0
        if admins<=1: flash("The last admin account cannot be converted to a normal user.","error"); return redirect(url_for("admin_user_details",user_id=user.id))
    user.role=role; db.session.commit(); flash("User role updated successfully.","success"); return redirect(url_for("admin_user_details",user_id=user.id))

@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    user=db.session.get(User,user_id)
    if not user: flash("User not found.","error"); return redirect(url_for("admin_users"))
    if user.id==session["user_id"]: flash("You cannot delete your own admin account.","error"); return redirect(url_for("admin_user_details",user_id=user.id))
    if user.role=="admin":
        admins=db.session.scalar(db.select(db.func.count()).select_from(User).where(User.role=="admin")) or 0
        if admins<=1: flash("The last admin account cannot be deleted.","error"); return redirect(url_for("admin_user_details",user_id=user.id))
    for row in db.session.execute(db.select(PasswordResetToken).where(PasswordResetToken.user_id==user.id)).scalars().all(): db.session.delete(row)
    for row in db.session.execute(db.select(LoginHistory).where(LoginHistory.user_id==user.id)).scalars().all(): db.session.delete(row)
    db.session.delete(user); db.session.commit(); flash("User deleted successfully.","success"); return redirect(url_for("admin_users"))

@app.route("/admin/login-history")
@admin_required
def admin_login_history():
    page=request.args.get("page",1,type=int); stmt=db.select(LoginHistory).order_by(LoginHistory.login_time.desc()); pagination=db.paginate(stmt,page=page,per_page=20,error_out=False)
    return render_template("admin/login_history.html", records=pagination.items, pagination=pagination)

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["X-Frame-Options"]="SAMEORIGIN"
    response.headers["Referrer-Policy"]="strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"]="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; form-action 'self'; frame-ancestors 'self';"
    if IS_PRODUCTION: response.headers["Strict-Transport-Security"]="max-age=31536000; includeSubDomains"
    return response

@app.errorhandler(CSRFError)
def csrf_error(error): return render_template("errors/400.html", message="Your form session expired or the request was invalid. Please try again."),400
@app.errorhandler(403)
def forbidden(error): return render_template("errors/403.html"),403
@app.errorhandler(404)
def not_found(error): return render_template("errors/404.html"),404
@app.errorhandler(500)
def server_error(error): db.session.rollback(); return render_template("errors/500.html"),500

with app.app_context(): db.create_all()

if __name__ == "__main__":
    app.run(debug=not IS_PRODUCTION)
