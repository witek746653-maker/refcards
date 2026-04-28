import sqlite3, os, glob
conn = sqlite3.connect('refcards.db')
db = conn.cursor()
try:
    db.execute('ALTER TABLE cards ADD COLUMN filepath TEXT')
except:
    pass
cards = db.execute('SELECT id, name FROM cards WHERE filepath IS NULL').fetchall()
files = glob.glob(os.path.abspath(os.path.join('..', 'cards', '*.md')))
matched = 0
for cid, name in cards:
    for f in files:
        if os.path.basename(f).replace('.md', '') == name or name in f:
            db.execute('UPDATE cards SET filepath=? WHERE id=?', (f, cid))
            matched += 1
            break
conn.commit()
print(f'Matched {matched} existing cards')
