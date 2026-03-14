"""
Refcards v2 — общая библиотека на SQLite
Запуск: python server.py
Открыть: http://localhost:5100
"""

from flask import Flask, request, send_file, send_from_directory, jsonify # type: ignore
import markdown # type: ignore
from bs4 import BeautifulSoup # type: ignore
from weasyprint import HTML as WP_HTML # type: ignore
import warnings, os, io, sqlite3, uuid
from datetime import datetime, timezone

warnings.filterwarnings("ignore")
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.abspath(os.environ.get("REFCARDS_FRONTEND", os.path.join(BASE_DIR, "..", "frontend"))))

DB_PATH     = os.path.join(BASE_DIR, "refcards.db")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

@app.after_request
def add_cors(response):
    origin = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return '', 204


# ── БД ──────────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id         TEXT PRIMARY KEY,
                name       TEXT NOT NULL DEFAULT 'Без названия',
                domain     TEXT NOT NULL DEFAULT 'default',
                content    TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        db.commit()

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── Темы ────────────────────────────────────────────────────────────────────

THEMES = {
    "programming":           {"p":"#0f3460","h1l":"#e94560","h2b":"#0f3460","h2t":"#fff","h3b":"#e8f0fe","h3br":"#4361ee","h3t":"#0f3460","cb":"#1a1a2e","ct":"#e2e8f8","cbr":"#4361ee","ib":"#e8f0fe","it":"#0f3460","th":"#0f3460","te":"#f0f4ff","qb":"#fff8e7","qbr":"#f4a261","qt":"#4a3800","body":"#1a1a2e","fb":"'IBM Plex Sans',sans-serif","fm":"'IBM Plex Mono',monospace","fh":"'IBM Plex Sans',sans-serif","ac":"#4361ee","cols":2,"bpt":8.0,"cpt":6.8},
    "language_fr":           {"p":"#5c1a1a","h1l":"#e67e22","h2b":"#5c1a1a","h2t":"#fff5e6","h3b":"#fff0e0","h3br":"#c0392b","h3t":"#5c1a1a","cb":"#fff5e6","ct":"#5c1a1a","cbr":"#e67e22","ib":"#fdebd0","it":"#5c1a1a","th":"#7b2d00","te":"#fff5e6","qb":"#fef9f0","qbr":"#e67e22","qt":"#5c1a1a","body":"#2c1810","fb":"'Lora','Georgia',serif","fm":"'IBM Plex Sans',sans-serif","fh":"'IBM Plex Sans',sans-serif","ac":"#c0392b","cols":2,"bpt":8.5,"cpt":7.5},
    "language_en":           {"p":"#1a3a4a","h1l":"#00acc1","h2b":"#1a3a4a","h2t":"#e0f7f4","h3b":"#e0f2f1","h3br":"#00897b","h3t":"#1a3a4a","cb":"#e8f5f4","ct":"#1a3a4a","cbr":"#00acc1","ib":"#e0f2f1","it":"#00695c","th":"#00695c","te":"#e8f5e9","qb":"#f0fbff","qbr":"#00acc1","qt":"#004d5a","body":"#1a2a2a","fb":"'IBM Plex Sans',sans-serif","fm":"'IBM Plex Sans',sans-serif","fh":"'IBM Plex Sans',sans-serif","ac":"#00897b","cols":2,"bpt":8.5,"cpt":7.5},
    "art":                   {"p":"#3d0c02","h1l":"#b8860b","h2b":"#3d0c02","h2t":"#fdf6e3","h3b":"#fdf6e3","h3br":"#b8860b","h3t":"#3d0c02","cb":"#fdf6e3","ct":"#3d0c02","cbr":"#b8860b","ib":"#fef9e7","it":"#5c3d02","th":"#5c2000","te":"#fdf6e3","qb":"#fffbf0","qbr":"#b8860b","qt":"#3d2b00","body":"#1a0a00","fb":"'Lora','Georgia',serif","fm":"'IBM Plex Sans',sans-serif","fh":"'IBM Plex Sans',sans-serif","ac":"#b8860b","cols":2,"bpt":8.5,"cpt":7.5},
    "literature_fiction":    {"p":"#1a3a1a","h1l":"#d4800a","h2b":"#1a3a1a","h2t":"#f5f5dc","h3b":"#f0f7ec","h3br":"#4a7c59","h3t":"#1a3a1a","cb":"#faf7f0","ct":"#2c1f00","cbr":"#d4800a","ib":"#f5f5dc","it":"#2c1f00","th":"#2d5a27","te":"#f0f7ec","qb":"#fdf8ef","qbr":"#d4800a","qt":"#3d2b00","body":"#1a1a0a","fb":"'Lora','Georgia',serif","fm":"'IBM Plex Sans',sans-serif","fh":"'IBM Plex Sans',sans-serif","ac":"#d4800a","cols":2,"bpt":8.5,"cpt":7.5},
    "literature_nonfiction": {"p":"#1c3557","h1l":"#4a90a4","h2b":"#1c3557","h2t":"#e8f4f8","h3b":"#e8f4f8","h3br":"#4a90a4","h3t":"#1c3557","cb":"#f0f7fb","ct":"#1c3557","cbr":"#4a90a4","ib":"#ddeef5","it":"#1c3557","th":"#1c3557","te":"#eef6fa","qb":"#f5fbff","qbr":"#4a90a4","qt":"#1c3557","body":"#1a1a2a","fb":"'IBM Plex Sans',sans-serif","fm":"'IBM Plex Sans',sans-serif","fh":"'IBM Plex Sans',sans-serif","ac":"#4a90a4","cols":2,"bpt":8.0,"cpt":7.0},
    "culture":               {"p":"#1a4a4a","h1l":"#e07a5f","h2b":"#1a4a4a","h2t":"#f7ede8","h3b":"#fdf0ec","h3br":"#e07a5f","h3t":"#1a4a4a","cb":"#fdf0ec","ct":"#3d1a0a","cbr":"#e07a5f","ib":"#fde8e0","it":"#3d1a0a","th":"#1a4a4a","te":"#fdf0ec","qb":"#f7fafa","qbr":"#2a9d8f","qt":"#1a4a4a","body":"#1a1a1a","fb":"'IBM Plex Sans',sans-serif","fm":"'IBM Plex Sans',sans-serif","fh":"'IBM Plex Sans',sans-serif","ac":"#e07a5f","cols":2,"bpt":8.5,"cpt":7.5},
    "psychology":            {"p":"#2d1b69","h1l":"#9b72cf","h2b":"#2d1b69","h2t":"#f0eaff","h3b":"#f0eaff","h3br":"#7c5cbf","h3t":"#2d1b69","cb":"#f5f0ff","ct":"#2d1b69","cbr":"#9b72cf","ib":"#ede8ff","it":"#2d1b69","th":"#2d1b69","te":"#f5f0ff","qb":"#fdf8ff","qbr":"#9b72cf","qt":"#2d1b69","body":"#1a1020","fb":"'IBM Plex Sans',sans-serif","fm":"'IBM Plex Sans',sans-serif","fh":"'IBM Plex Sans',sans-serif","ac":"#7c5cbf","cols":2,"bpt":8.5,"cpt":7.5},
    "lyrics":                {"p":"#2c3e50","h1l":"#7f8c8d","h2b":"#2c3e50","h2t":"#fff","h3b":"#f9f9f9","h3br":"#95a5a6","h3t":"#2c3e50","cb":"#fff","ct":"#2c3e50","cbr":"#bdc3c7","ib":"#f4f4f4","it":"#2c3e50","th":"#2c3e50","te":"#f9f9f9","qb":"#fff","qbr":"#7f8c8d","qt":"#2c3e50","body":"#1a1a1a","fb":"'Lora',serif","fm":"'IBM Plex Sans',sans-serif","fh":"'Lora',serif","ac":"#2980b9","cols":2,"bpt":9.0,"cpt":8.0},
    "default":               {"p":"#2c3e50","h1l":"#e74c3c","h2b":"#2c3e50","h2t":"#fff","h3b":"#eaf2fb","h3br":"#3498db","h3t":"#2c3e50","cb":"#1a1a2e","ct":"#e2e8f8","cbr":"#3498db","ib":"#eaf2fb","it":"#2c3e50","th":"#2c3e50","te":"#eaf2fb","qb":"#fef9e7","qbr":"#f39c12","qt":"#4a3800","body":"#1a1a2e","fb":"'IBM Plex Sans',sans-serif","fm":"'IBM Plex Mono',monospace","fh":"'IBM Plex Sans',sans-serif","ac":"#3498db","cols":2,"bpt":8.0,"cpt":6.8},
}

CSS_TMPL = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;0,700;1,400&family=Lora:ital,wght@0,400;0,600;0,700;1,400&display=swap');
@page {{ size:A4; margin:10mm 11mm; @bottom-right {{ content:counter(page); font-family:{fb}; font-size:7pt; color:#aaa; }} }}
*{{box-sizing:border-box}}
body{{font-family:{fb};font-size:{bpt}pt;line-height:1.35;color:{body};background:white;column-count:{cols};column-gap:8mm;column-fill:balance;text-align:justify;hyphens:auto;padding:0;margin:0}}
h1{{column-span:all;font-family:{fh};font-size:13pt;font-weight:700;color:{p};border-bottom:2px solid {h1l};padding-bottom:3px;margin:0 0 2px 0;break-after:avoid}}
h1+p{{column-span:all;font-style:italic;color:#666;font-size:7.5pt;margin:0 0 6px 0}}
h2{{column-span:all;font-family:{fh};font-size:9pt;font-weight:700;color:{h2t};background:{h2b};padding:3px 7px;margin:15px 0 8px 0;break-after:avoid;border-radius:2px}}
h3{{font-family:{fh};font-size:8pt;font-weight:700;color:{h3t};background:{h3b};border-left:3px solid {h3br};padding:2px 6px;margin:12px 0 6px 0;break-after:avoid;border-radius:0 2px 2px 0}}
h4{{font-size:7.5pt;font-weight:700;color:{p};margin:10px 0 4px 0;break-after:avoid}}
.section-h3{{break-inside:avoid;page-break-inside:avoid}}
p{{margin:0 0 3px 0}}
pre{{background:{cb};color:{ct};border-radius:3px;padding:4px 7px;font-family:{fm};font-size:{cpt}pt;line-height:1.3;margin:8px 0;break-inside:auto;page-break-inside:auto;border-left:2px solid {cbr};white-space:pre-wrap;word-break:break-all;width:100%;overflow:hidden}}
code{{font-family:{fm};background:{ib};color:{it};padding:0 3px;border-radius:2px;font-size:{cpt}pt}}
pre code{{background:none;color:inherit;padding:0}}
table{{width:100%;border-collapse:collapse;margin:10px 0;font-size:7pt;break-inside:auto;page-break-inside:auto;overflow:hidden}}
thead tr{{background:{th};color:white}}
thead th{{padding:3px 5px;text-align:left;font-weight:600}}
tbody tr:nth-child(even){{background:{te}}}
tbody tr:nth-child(odd){{background:white}}
tbody td{{padding:2px 5px;border-bottom:1px solid #dde;vertical-align:top}}
blockquote{{background:{qb};border-left:3px solid {qbr};margin:10px 0;padding:5px 10px;border-radius:0 3px 3px 0;font-size:7.5pt;color:{qt};break-inside:auto;page-break-inside:auto;font-style:italic;width:100%;overflow:hidden}}
blockquote p{{margin:0}}
ul,ol{{margin:8px 0;padding-left:14px;break-inside:auto;page-break-inside:auto}}
li{{margin-bottom:2px;line-height:1.3;break-inside:auto;page-break-inside:auto}}
strong{{font-weight:700;color:{p}}}
em{{color:#555}}
hr{{border:none;border-top:1px solid #dde;margin:4px 0}}
a{{color:{ac}}}
"""

def parse_front_matter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            meta = {}
            for line in text[3:end].strip().split("\n"): # type: ignore
                i = line.find(":")
                if i > 0:
                    meta[line[:i].strip()] = line[i+1:].strip()
            return meta, text[end+4:].lstrip() # type: ignore
    return {}, text

def wrap_sections(html_body):
    soup = BeautifulSoup(html_body, "html.parser")
    def group_by(elements, tag_name, div_class):
        groups, current, has_h = [], [], False
        for el in elements:
            if getattr(el, "name", None) == tag_name:
                if current: groups.append((has_h, current))
                current, has_h = [el], True
            else:
                current.append(el)
        if current: groups.append((has_h, current))
        result = []
        for has_h, bucket in groups:
            if not has_h:
                result.extend(bucket)
            else:
                div = soup.new_tag("div", attrs={"class": div_class})
                for el in bucket:
                    div.append(el.extract() if hasattr(el, "extract") else el)
                result.append(div)
        return result
    h2_sections = group_by(list(soup.contents), "h2", "section-h2")
    final = []
    for el in h2_sections:
        if hasattr(el, "get") and "section-h2" in (el.get("class") or []):
            h3_grouped = group_by(list(el.contents), "h3", "section-h3")
            el.clear()
            for child in h3_grouped: el.append(child)
        final.append(el)
    wrapper = BeautifulSoup("", "html.parser")
    for el in final: wrapper.append(el)
    return str(wrapper)

def build_pdf(markdown_text):
    meta, content = parse_front_matter(markdown_text)
    domain  = meta.get("domain", "default")
    density = meta.get("density", "medium")
    t    = THEMES.get(domain, THEMES["default"])
    # Явное приведение типов для линтера
    base_bpt = float(t.get("bpt", 8.0))
    adj = 0.0
    if density == "high": adj = -0.5
    elif density == "low": adj = 0.5
    bpt  = base_bpt + adj
    cols = int(t.get("cols", 2)) if density != "low" else 1
    ctx  = dict(t)
    ctx["bpt"] = bpt
    ctx["cols"] = cols
    css  = CSS_TMPL.format(**ctx)
    md   = markdown.Markdown(extensions=["tables","fenced_code","nl2br"])
    raw  = md.convert(content)
    body = wrap_sections(raw)
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
    return WP_HTML(string=html).write_pdf()


# ════════════════════════════════════════════════════════════════════════════
# REST API — карточки
# ════════════════════════════════════════════════════════════════════════════

@app.route("/api/cards", methods=["GET"])
def cards_list():
    with get_db() as db:
        rows = db.execute(
            "SELECT id,name,domain,updated_at,created_at FROM cards ORDER BY updated_at DESC"
        ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/cards", methods=["POST"])
def cards_create():
    data = request.get_json(force=True)
    cid  = str(uuid.uuid4())
    ts   = now_iso()
    with get_db() as db:
        db.execute(
            "INSERT INTO cards (id,name,domain,content,created_at,updated_at) VALUES (?,?,?,?,?,?)",
            (cid, data.get("name","Новая карточка"), data.get("domain","default"),
             data.get("content",""), ts, ts)
        )
        db.commit()
    return jsonify({"id":cid,"name":data.get("name"),"domain":data.get("domain"),
                    "created_at":ts,"updated_at":ts}), 201

@app.route("/api/cards/<cid>", methods=["GET"])
def cards_get(cid):
    with get_db() as db:
        row = db.execute("SELECT * FROM cards WHERE id=?", (cid,)).fetchone()
    if not row: return jsonify({"error":"not found"}), 404
    return jsonify(dict(row))

@app.route("/api/cards/<cid>", methods=["PUT"])
def cards_update(cid):
    with get_db() as db:
        row = db.execute("SELECT * FROM cards WHERE id=?", (cid,)).fetchone()
        if not row: return jsonify({"error":"not found"}), 404
        data = request.get_json(force=True)
        name    = data.get("name",    row["name"])
        domain  = data.get("domain",  row["domain"])
        content = data.get("content", row["content"])
        ts = now_iso()
        db.execute("UPDATE cards SET name=?,domain=?,content=?,updated_at=? WHERE id=?",
                   (name, domain, content, ts, cid))
        db.commit()
    return jsonify({"id":cid,"name":name,"domain":domain,"updated_at":ts})

@app.route("/api/cards/<cid>", methods=["DELETE"])
def cards_delete(cid):
    with get_db() as db:
        db.execute("DELETE FROM cards WHERE id=?", (cid,))
        db.commit()
    return jsonify({"deleted":cid})

# ── PDF ──────────────────────────────────────────────────────────────────────

@app.route("/api/pdf", methods=["POST"])
def api_pdf():
    data     = request.get_json(force=True)
    md_text  = data.get("markdown","")
    filename = "".join(c for c in data.get("filename","refcard") if c.isalnum() or c in "-_ ").strip()
    filename = (filename.replace(" ","-") or "refcard")
    pdf      = build_pdf(md_text)
    return send_file(io.BytesIO(pdf), mimetype="application/pdf",
                     as_attachment=True, download_name=f"{filename}.pdf")

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files: return jsonify({"error":"no file"}), 400
    file = request.files['file']
    if not file.filename: return jsonify({"error":"no filename"}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower()
    fname = f"{uuid.uuid4()}.{ext}"
    file.save(os.path.join(UPLOADS_DIR, fname))
    return jsonify({"url": f"/uploads/{fname}"})

@app.route("/uploads/<path:filename>")
def get_upload(filename):
    return send_from_directory(UPLOADS_DIR, filename)

@app.route("/api/cards/import", methods=["POST"])
def cards_import():
    if 'files' not in request.files: return jsonify({"error":"no files"}), 400
    files = request.files.getlist('files')
    imported = []
    with get_db() as db:
        for file in files:
            if not file.filename.endswith('.md'): continue
            content = file.read().decode('utf-8', errors='ignore')
            meta, body = parse_front_matter(content)
            
            cid  = str(uuid.uuid4())
            ts   = now_iso()
            # Имя: из метаданных или имя файла без расширения
            name = meta.get("name", file.filename.rsplit('.', 1)[0])
            domain = meta.get("domain", "default")
            
            db.execute(
                "INSERT INTO cards (id,name,domain,content,created_at,updated_at) VALUES (?,?,?,?,?,?)",
                (cid, name, domain, content, ts, ts)
            )
            imported.append({"id":cid, "name":name})
        db.commit()
    return jsonify({"imported": imported}), 201

# ── Статика ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder,"index.html")

@app.route("/api/health")
def health():
    with get_db() as db:
        count = db.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
    return jsonify({"ok":True,"cards":count,"version":"2.0"})

if __name__ == "__main__":
    init_db()
    print("\n  Refcards v2  →  http://localhost:5100\n")
    app.run(host="127.0.0.1", port=5100, debug=False)
