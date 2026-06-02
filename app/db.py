from contextlib import contextmanager
from pathlib import Path
import pymysql
from flask import current_app
from werkzeug.security import generate_password_hash


@contextmanager
def db_cursor():
    cfg = current_app.config
    con = pymysql.connect(
        host=cfg["DB_HOST"],
        port=cfg["DB_PORT"],
        user=cfg["DB_USER"],
        password=cfg["DB_PASSWORD"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    try:
        cur = con.cursor()
        cur.execute(f"USE {cfg['DB_NAME']}")
        yield con, cur
    finally:
        con.close()


def init_db():
    base_dir = Path(current_app.config["BASE_DIR"])
    sql_path = base_dir / "schema.sql"
    sql = sql_path.read_text(encoding="utf-8")

    cfg = current_app.config
    con = pymysql.connect(
        host=cfg["DB_HOST"],
        port=cfg["DB_PORT"],
        user=cfg["DB_USER"],
        password=cfg["DB_PASSWORD"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    try:
        cur = con.cursor()
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            cur.execute(stmt)
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def ensure_seed():
    with db_cursor() as (con, cur):
        cur.execute("SELECT id FROM admins WHERE username='admin'")
        if cur.fetchone() is None:
            pw = generate_password_hash("password")
            cur.execute(
                "INSERT INTO admins (username,password,name) VALUES (%s,%s,%s)",
                ("admin", pw, "Administrator"),
            )

        cur.execute("SELECT id FROM users WHERE username='user'")
        if cur.fetchone() is None:
            pw = generate_password_hash("password")
            cur.execute(
                "INSERT INTO users (username,password,name) VALUES (%s,%s,%s)",
                ("user", pw, "Demo User"),
            )

        cur.execute("SELECT id FROM users WHERE username='alice'")
        if cur.fetchone() is None:
            pw = generate_password_hash("password")
            cur.execute(
                "INSERT INTO users (username,password,name) VALUES (%s,%s,%s)",
                ("alice", pw, "Alice"),
            )

        cur.execute("SELECT id FROM users WHERE username='user'")
        uid = cur.fetchone()["id"]
        cur.execute("SELECT id FROM users WHERE username='alice'")
        aid = cur.fetchone()["id"]

        cur.execute(
            "SELECT id FROM friends WHERE user_id=%s AND friend_id=%s", (uid, aid)
        )
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO friends (user_id,friend_id) VALUES (%s,%s)", (uid, aid)
            )
        cur.execute(
            "SELECT id FROM friends WHERE user_id=%s AND friend_id=%s", (aid, uid)
        )
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO friends (user_id,friend_id) VALUES (%s,%s)", (aid, uid)
            )

        cur.execute("SELECT id FROM moments WHERE user_id=%s", (uid,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO moments (user_id,content) VALUES (%s,%s)",
                (uid, "Hello from Demo User"),
            )
            mid = cur.lastrowid
            cur.execute(
                "INSERT INTO comments (moment_id,user_id,content) VALUES (%s,%s,%s)",
                (mid, aid, "Nice post"),
            )

        con.commit()
