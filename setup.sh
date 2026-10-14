#!/bin/bash
# Blog Website Setup Script

echo "🚀 Setting up Blog Website..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install flask flask-sqlalchemy werkzeug

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static/uploads
mkdir -p instance

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from app import app, db, Admin; app.app_context().push(); db.create_all()"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 To start the website, run:"
echo "   source venv/bin/activate  # On Windows: venv\Scripts\activate"
echo "   python app.py"
echo ""
echo "📍 Then open your browser to:"
echo "   http://localhost:5000"
echo ""
echo "🔐 Admin login:"
echo "   URL: http://localhost:5000/admin/login"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
