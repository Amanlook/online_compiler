# Online Python Compiler

A modern, web-based Python compiler built with FastAPI that allows users to write, execute, and see the output of Python code in a beautiful, responsive interface.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd online_compiler


# Access the application
open http://localhost:8888
```


## ✨ Features

- **🎨 Modern Web Interface**: Beautiful, responsive design with syntax highlighting
- **⚡ Real-time Execution**: Instant Python code compilation and execution
- **🔒 Secure Processing**: Timeout protection and process isolation
- **📱 Mobile Friendly**: Responsive design that works on all devices
- **⌨️ Keyboard Shortcuts**: Ctrl+Enter (Cmd+Enter) to run code
- **🐳 Docker Ready**: Complete containerization support
- **📊 API Access**: RESTful endpoints for programmatic usage
- **🔍 Auto Documentation**: Interactive API docs with Swagger UI

## Usage

1. Open the web interface at `http://localhost:8888`
2. Write your Python code in the editor (with syntax highlighting)
3. Click "Run Code" to execute or use Ctrl+Enter (Cmd+Enter on Mac)
4. View the output or error messages in the output panel
5. Use the "Clear" button to reset the output

## Features

- **Web-based Python code editor** with syntax highlighting (CodeMirror)
- **Real-time code execution** with proper error handling
- **Output display** with success/error indication
- **Simple and clean interface** with responsive design
- **Keyboard shortcuts** (Ctrl+Enter / Cmd+Enter to run code)
- **API endpoints** for programmatic access
- **Built with FastAPI** for high performance

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.8+)
- **Frontend**: HTML5, CSS3, JavaScript
- **Editor**: CodeMirror with Python syntax highlighting
- **Environment**: UV for package management

## 📦 Project Structure

```
online_compiler/
├── 📄 main.py                 # FastAPI application
├── 📁 templates/              # HTML templates
│   └── index.html            # Main web interface
├── 📁 static/                # Static assets
│   ├── style.css             # Styling
│   └── script.js             # Frontend logic
├── 📋 pyproject.toml         # Project configuration
```

## Setup

1. Install uv if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create and activate virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

## Running the Application
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the server
python main.py
```

### Option 3: Using uvicorn directly
```bash
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8888
```


Then open your browser and navigate to `http://localhost:8888`

## API Endpoints

- `GET /` - Main interface
- `POST /compile` - Execute Python code
- `GET /docs` - FastAPI automatic documentation


## Security Note

This is a basic implementation for educational purposes. For production use, consider implementing proper sandboxing and security measures when executing user code.
