# Refcards

A Markdown-based reference card editor and PDF exporter.

## 📝 Overview
Refcards is a tool for creating, managing, and exporting high-quality A4 PDF reference cards (cheat sheets). It uses a Flask backend to render Markdown content into structured PDF layouts using WeasyPrint.

## 🚀 Features
- **Markdown Editor**: Write cards using standard Markdown.
- **PDF Export**: Generate print-ready A4 PDFs with professional styling.
- **Modular Content**: Specialized modules for Art, History, Programming, Philosophy, and more.
- **Web UI**: Centralized dashboard for managing all reference cards.
- **Deployment Ready**: Includes scripts for server synchronization and automated backups.

## 🛠 Tech Stack
- **Backend**: Python 3, Flask.
- **PDF Rendering**: WeasyPrint.
- **Frontend**: Vanilla HTML/JS.
- **Database**: SQLite (for metadata and card tracking).

## 📂 Project Structure
```text
refcards/
├── backend/             # Flask API and PDF generation logic
├── frontend/            # Dashboard UI
├── cards/               # Markdown source files for cards
├── scripts/             # Deployment and backup automation
├── SKILL.md             # Core skill and pattern definitions
└── Makefile             # Task automation
```

## 💻 Developer Instructions
### Local Development
1. **Prepare Environment**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. **Run Server**:
   ```bash
   REFCARDS_FRONTEND=../frontend python server.py
   ```
3. Access at `http://localhost:5100`.

### Deployment
- Use `bash scripts/push.sh <server_ip>` to sync changes to production.
- Use `bash scripts/backup-github.sh` to version control your content.

## 📄 License
Personal Project.
