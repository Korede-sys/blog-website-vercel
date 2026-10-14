from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re

app = Flask(__name__)
import os

# Use environment variable for database URL (PostgreSQL on Vercel, SQLite locally)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
# Fix for Heroku/Vercel PostgreSQL URLs
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("SECRET_KEY environment variable is not set!")app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)

# Database Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(200))
    category = db.Column(db.String(50), default='General')
    tags = db.Column(db.String(200))
    status = db.Column(db.String(20), default='draft')  # draft or published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('admin.id'))

    def __repr__(self):
        return f'<Post {self.title}>'

# Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_slug(title):
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug.strip('-')

def is_logged_in():
    return session.get('admin_id') is not None

def get_current_admin():
    if is_logged_in():
        return Admin.query.get(session['admin_id'])
    return None

# Context processor to make variables available in all templates
@app.context_processor
def inject_globals():
    return {
        'current_admin': get_current_admin(),
        'current_year': datetime.now().year
    }

# Routes
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(status='published')\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=6, error_out=False)
    return render_template('index.html', posts=posts)

@app.route('/post/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()
    return render_template('post.html', post=post)

@app.route('/category/<category>')
def category(category):
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(status='published', category=category)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=6, error_out=False)
    return render_template('index.html', posts=posts, category=category)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    if query:
        posts = Post.query.filter(
            Post.status == 'published',
            (Post.title.contains(query)) | (Post.content.contains(query))
        ).order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=6, error_out=False)
    else:
        posts = None
    return render_template('search.html', posts=posts, query=query)

# Admin Authentication Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_logged_in():
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Admin Dashboard Routes
@app.route('/admin')
def admin_dashboard():
    if not is_logged_in():
        return redirect(url_for('admin_login'))

    posts = Post.query.order_by(Post.created_at.desc()).all()
    published_count = Post.query.filter_by(status='published').count()
    draft_count = Post.query.filter_by(status='draft').count()

    return render_template('admin/dashboard.html', 
                         posts=posts, 
                         published_count=published_count, 
                         draft_count=draft_count)

@app.route('/admin/post/new', methods=['GET', 'POST'])
def admin_new_post():
    if not is_logged_in():
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category', 'General')
        tags = request.form.get('tags')
        status = request.form.get('status', 'draft')

        # Handle featured image upload
        featured_image = None
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to make filename unique
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                featured_image = filename

        slug = generate_slug(title)
        # Ensure slug is unique
        original_slug = slug
        counter = 1
        while Post.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1

        post = Post(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            featured_image=featured_image,
            category=category,
            tags=tags,
            status=status,
            author_id=session['admin_id']
        )

        db.session.add(post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/new_post.html')

@app.route('/admin/post/edit/<int:post_id>', methods=['GET', 'POST'])
def admin_edit_post(post_id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))

    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.excerpt = request.form.get('excerpt')
        post.category = request.form.get('category', 'General')
        post.tags = request.form.get('tags')
        post.status = request.form.get('status', 'draft')
        post.updated_at = datetime.utcnow()

        # Handle new featured image
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename and allowed_file(file.filename):
                # Delete old image if exists
                if post.featured_image:
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.featured_image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                post.featured_image = filename

        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_post.html', post=post)

@app.route('/admin/post/delete/<int:post_id>', methods=['POST'])
def admin_delete_post(post_id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))

    post = Post.query.get_or_404(post_id)

    # Delete featured image if exists
    if post.featured_image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.featured_image)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(post)
    db.session.commit()

    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# API endpoint for dark mode preference (optional - can be handled client-side)
@app.route('/api/toggle-theme', methods=['POST'])
def toggle_theme():
    theme = request.json.get('theme')
    session['theme'] = theme
    return jsonify({'status': 'success', 'theme': theme})

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        if not Admin.query.filter_by(username=admin_username).first():
            admin = Admin(
                username=admin_username,
                password_hash=generate_password_hash(admin_password)
            )
            db.session.add(admin)
            db.session.commit()
            print(f'Default admin created: username={admin_username}')

# For Vercel serverless deployment
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

# Vercel handler
handler = app
