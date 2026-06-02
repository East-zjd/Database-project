def get_by_username(cur, username):
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    return cur.fetchone()


def get_by_id(cur, user_id):
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    return cur.fetchone()


def create_user(cur, username, password_hash):
    cur.execute(
        "INSERT INTO users (username,password) VALUES (%s,%s)",
        (username, password_hash),
    )


def update_profile(cur, user_id, name, gender, birthdate, age):
    cur.execute(
        "UPDATE users SET name=%s, gender=%s, birthdate=%s, age=%s WHERE id=%s",
        (name, gender, birthdate, age, user_id),
    )


def update_password(cur, user_id, password_hash):
    cur.execute("UPDATE users SET password=%s WHERE id=%s", (password_hash, user_id))


def search_by_username(cur, keyword):
    cur.execute(
        "SELECT id,username,name FROM users WHERE username LIKE %s LIMIT 20",
        (f"%{keyword}%",),
    )
    return cur.fetchall()


def delete_by_id(cur, user_id):
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))


def list_users(cur):
    cur.execute(
        "SELECT id,username,name,created_at FROM users ORDER BY created_at DESC"
    )
    return cur.fetchall()
