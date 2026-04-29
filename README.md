# Refcards

A Markdown-based reference card editor and library manager.

## 📝 Overview
Refcards is a tool for creating, managing, and exporting Markdown reference cards (cheat sheets). It uses a Flask backend to serve cards and synchronizes text files with a local SQLite database, establishing a "Single Source of Truth" workflow.

## 🚀 Features
- **Markdown Editor**: Write cards using standard Markdown.
- **Direct Markdown Export**: Download cards directly as `.md` files without complex dependencies.
- **Modular Content**: Specialized modules for Art, History, Programming, Philosophy, and more.
- **Web UI**: Centralized dashboard for managing all reference cards.
- **Smart Synchronization**: One-click sync button updates the internal database from raw `.md` files.

## 🛠 Tech Stack
- **Backend**: Python 3, Flask.
- **Frontend**: Vanilla HTML/JS.
- **Database**: SQLite (for metadata and fast card fetching).

## 📂 Project Structure
```text
refcards/
├── backend/             # Flask API and sync logic
├── frontend/            # Dashboard UI
├── cards/               # Markdown source files for cards (Single Source of Truth)
├── scripts/             # Deployment and automation tools
├── SKILL.md             # Core skill and pattern definitions
└── Makefile             # Task automation
```

## 💻 Developer Instructions
### Local Development
1. **Prepare Environment**:
   ```bash
   cd backend
   python -m venv venv
   # source venv/bin/activate (Linux/Mac) or venv\Scripts\activate (Windows)
   pip install -r requirements.txt
   ```
2. **Run Server**:
   ```bash
   python server.py
   ```
3. Access at `http://localhost:5100`.

### Deployment & Synchronization
Мы используем Git для доставки файлов и кода на удалённый сервер:
1. **Локально**: `git add .`, `git commit`, `git push` (или алиас `git up`).
2. **На сервере**: Подключиться по SSH, перейти в папку проекта и выполнить `git pull`.
3. **Обновление БД**: Зайти в веб-интерфейс (по IP сервера) и нажать кнопку синхронизации, чтобы база данных загрузила новые `.md` файлы.

## 📄 License
Personal Project.
