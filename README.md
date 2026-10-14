# 📝 Blog Website with Admin Panel & Dark Mode

A complete, production-ready blog website built with Flask. Features include admin authentication, content management, image uploads, search, categories, and a beautiful dark mode toggle.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌙 **Dark Mode** | Toggle between light and dark themes, preference saved |
| 🔐 **Admin Login** | Secure authentication with password hashing |
| ✍️ **Create Posts** | Rich post editor with title, content, excerpt, category, tags |
| ✏️ **Edit Posts** | Update any field, replace featured image |
| 🗑️ **Delete Posts** | With confirmation dialog |
| 📷 **Image Upload** | Featured image with live preview |
| 🔍 **Search** | Search posts by title or content |
| 📂 **Categories** | Filter posts by category |
| 📄 **Pagination** | Automatic pagination for blog listing |
| 📊 **Dashboard** | Stats overview and post management table |
| 🏷️ **Tags** | Add tags to posts for better organization |
| 📱 **Responsive** | Works on desktop, tablet, and mobile |

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)

**On macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**On Windows:**
```cmd
setup.bat
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scriptsctivate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install flask flask-sqlalchemy werkzeug

# 4. Run the application
python app.py
```

## 📍 Access the Website

| URL | Description |
|-----|-------------|
| `http://localhost:5000` | Blog homepage |
| `http://localhost:5000/admin` | Admin dashboard |
| `http://localhost:5000/admin/login` | Admin login page |

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change the default password after first login!

## 📁 Project Structure

```
blog-website/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── setup.sh                  # Linux/macOS setup script
├── setup.bat                 # Windows setup script
├── README.md                 # This file
├── instance/
│   └── blog.db               # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css         # Styles with CSS variables for theming
│   ├── js/
│   │   └── main.js           # Dark mode toggle & interactions
│   └── uploads/              # Uploaded images
└── templates/
    ├── base.html             # Base template with navbar
    ├── index.html            # Blog homepage
    ├── post.html             # Single post page
    ├── search.html           # Search results
    └── admin/
        ├── login.html        # Admin login
        ├── dashboard.html    # Post management
        ├── new_post.html     # Create post
        └── edit_post.html    # Edit post
```

## 🔧 Configuration

### Change Secret Key

Edit `app.py` and replace:
```python
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
```

With a random string:
```python
import secrets
app.config['SECRET_KEY'] = secrets.token_hex(32)
```

### Change Admin Password

After logging in, you can modify the password directly in the database or add a password change feature.

### Database

The project uses SQLite by default. To use PostgreSQL or MySQL:

```python
# PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/blogdb'

# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/blogdb'
```

## 🎨 Customization

### Change Colors

Edit `static/css/style.css` and modify the CSS variables:

```css
:root {
    --accent-color: #0d6efd;        /* Change primary color */
    --bg-primary: #ffffff;          /* Change background */
    --text-primary: #212529;        /* Change text color */
}

[data-theme="dark"] {
    --accent-color: #0d6efd;
    --bg-primary: #1a1a2e;
    --text-primary: #e9ecef;
}
```

### Add New Categories

Edit the category select in `templates/admin/new_post.html` and `templates/admin/edit_post.html`:

```html
<option value="YourCategory">Your Category</option>
```

## 🛡️ Security Recommendations

1. **Change default credentials** immediately
2. **Use environment variables** for sensitive data:
   ```python
   import os
   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
   ```
3. **Enable HTTPS** in production
4. **Add rate limiting** to login attempts
5. **Validate and sanitize** all user inputs
6. **Use a production WSGI server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

## 🐛 Troubleshooting

### Database errors
```bash
# Delete and recreate database
rm instance/blog.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Port already in use
```bash
# Run on a different port
python app.py --port 5001
# Or edit app.py: app.run(debug=True, port=5001)
```

### Module not found
```bash
# Make sure virtual environment is activated
pip install flask flask-sqlalchemy werkzeug
```

## 📦 Deployment

### Heroku
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Create requirements.txt
pip freeze > requirements.txt

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku create
git push heroku main
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Made with ❤️ using Flask
