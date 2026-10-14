import os
import re
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# ---------------------------------------------------------------------------
# Application configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback-dev-key-change-me")

# Use DATABASE_URL for PostgreSQL in production. SQLite is for local development.
database_url = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

# Upload folder configuration
upload_folder = os.environ.get(
    "UPLOAD_FOLDER", str(Path(app.root_path) / "static" / "uploads")
)
app.config["UPLOAD_FOLDER"] = upload_folder
Path(upload_folder).mkdir(parents=True, exist_ok=True)

is_production = (
    os.environ.get("VERCEL") == "1"
    or os.environ.get("FLASK_ENV") == "production"
    or os.environ.get("FLASK_DEBUG") == "0"
)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=is_production,
)

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Database models
# ---------------------------------------------------------------------------

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(200))
    category = db.Column(db.String(50), default="General")
    tags = db.Column(db.String(200))
    status = db.Column(db.String(20), default="draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    author_id = db.Column(db.Integer, db.ForeignKey("admin.id"))

    def __repr__(self):
        return f"<Post {self.title}>"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

ALLOWED_FILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_FILE_EXTENSIONS


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    posts = Post.query.filter_by(status="published").order_by(Post.created_at.desc()).all()
    return render_template("index.html", posts=posts)


@app.route("/post/<slug>")
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, status="published").first_or_404()
    return render_template("post.html", post=post)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session["admin_id"] = admin.id
            session["username"] = admin.username
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "admin_id" not in session:
        return redirect(url_for("login"))
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("dashboard.html", posts=posts)


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
