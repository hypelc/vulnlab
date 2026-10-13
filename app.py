from flask import Flask, request, render_template_string, redirect, url_for, session, send_file, abort
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-me"

BASE = Path(__file__).resolve().parent
DB = BASE / "vulnlab.db"
FILES = BASE / "files"

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    cur = conn.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS notes;

    CREATE TABLE users(
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    );

    CREATE TABLE notes(
        id INTEGER PRIMARY KEY,
        owner_id INTEGER,
        title TEXT,
        content TEXT
    );
    """)
    cur.executemany(
        "INSERT INTO users(username,password,role) VALUES(?,?,?)",
        [
            ("alice","alice123","user"),
            ("bob","bob123","user"),
            ("admin","admin123","admin"),
        ],
    )
    cur.executemany(
        "INSERT INTO notes(owner_id,title,content) VALUES(?,?,?)",
        [
            (1,"Alice private note","alice-secret-demo"),
            (2,"Bob private note","bob-secret-demo"),
            (3,"Admin note","admin-secret-demo"),
        ],
    )
    conn.commit()
    conn.close()

def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    conn = db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return user

NAV = """
<div style="margin-bottom:16px">
<a href="/">Home</a> |
<a href="/login">Login</a> |
<a href="/search?q=test">Search</a> |
<a href="/notes/1">IDOR demo</a> |
<a href="/download?file=public.txt">Download demo</a> |
<a href="/admin">Admin</a> |
<a href="/logout">Logout</a>
</div>
"""

@app.route("/")
def home():
    user = current_user()
    who = f"Logged in as <b>{user['username']}</b>" if user else "Not logged in"
    return render_template_string(
        NAV + """
        <h1>VulnLab</h1>
        <p>{{ who|safe }}</p>
        <p>This application is intentionally vulnerable and must only be run locally.</p>
        <ul>
          <li>Login: intentionally vulnerable SQL query</li>
          <li>Notes: broken object-level authorization / IDOR</li>
          <li>Search: reflected XSS</li>
          <li>Download: path traversal</li>
          <li>Admin: weak authorization logic</li>
        </ul>
        """,
        who=who,
    )

@app.route("/login", methods=["GET","POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username","")
        password = request.form.get("password","")

        # INTENTIONALLY VULNERABLE: string concatenation into SQL.
        query = "SELECT * FROM users WHERE username = ? AND password = ?"


        conn = db()
        try:
            user = conn.execute(query, (username, password)).fetchone()
        except Exception as e:
            user = None
            message = f"Database error: {e}"
        conn.close()

        if user:
            session["uid"] = user["id"]
            return redirect(url_for("home"))
        if not message:
            message = "Invalid credentials"

    return render_template_string(
        NAV + """
        <h2>Login</h2>
        <p>Demo accounts: alice/alice123, bob/bob123</p>
        <form method="post">
          <label>Username <input name="username"></label><br><br>
          <label>Password <input name="password" type="password"></label><br><br>
          <button>Login</button>
        </form>
        <p>{{ message }}</p>
        """,
        message=message,
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/notes/<int:note_id>")
def note(note_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    conn = db()
    # INTENTIONALLY VULNERABLE: note ownership is not checked.
    note = conn.execute("SELECT * FROM notes WHERE id=? AND owner_id=?", (note_id, user["id"])).fetchone()
    conn.close()
    if not note:
        abort(404)

    return render_template_string(
        NAV + """
        <h2>{{ note['title'] }}</h2>
        <p>Owner ID: {{ note['owner_id'] }}</p>
        <pre>{{ note['content'] }}</pre>
        <p>Try changing the numeric note ID in the URL.</p>
        """,
        note=note,
    )

@app.route("/search")
def search():
    q = request.args.get("q","")
    # INTENTIONALLY VULNERABLE: unescaped user input.
    return render_template_string(
        NAV + """
        <h2Search</h2>

        <form method="get">
            <input name="q" value="{{ q }}">
            <button type="submit">Search</button>
        </form.

        <p>Results for: {{ q }}</p>
""",

q=q
    )

@app.route("/download")
def download():
    filename = request.args.get("file","public.txt")

    base_dir = FILES.resolve()

    target = (base_dir / filename).resolve()

    try:
        target.relative_to(base_dir)
    except ValueError:
        abort(403)

    if not target.is_file():
        abort(404)

    return send_file(target)

@app.route("/admin")
def admin():
    user = current_user()

    if not user:
        return redirect(url_for("login"))

    if user["role"] != "admin":
        abort(403)

    return render_template_string(
        NAV + """
        <h2>Admin panel</h2>
        <p>Restricted administrative area.</p>
        """,
    )


@app.route("/reset")
def reset():
    init_db()
    session.clear()
    return "Lab reset complete. <a href='/'>Return home</a>"

if __name__ == "__main__":
    FILES.mkdir(exist_ok=True)
    (FILES / "public.txt").write_text("This is a public demo file.\n")
    (BASE / "secret.txt").write_text("local-demo-secret\n")
    if not DB.exists():
        init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
