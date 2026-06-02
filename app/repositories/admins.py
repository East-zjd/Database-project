def get_by_username(cur, username):
    cur.execute("SELECT * FROM admins WHERE username=%s", (username,))
    return cur.fetchone()


def get_by_id(cur, admin_id):
    cur.execute("SELECT * FROM admins WHERE id=%s", (admin_id,))
    return cur.fetchone()


def update_profile(cur, admin_id, name, password_hash=None):
    if password_hash:
        cur.execute(
            "UPDATE admins SET name=%s, password=%s WHERE id=%s",
            (name, password_hash, admin_id),
        )
    else:
        cur.execute("UPDATE admins SET name=%s WHERE id=%s", (name, admin_id))
