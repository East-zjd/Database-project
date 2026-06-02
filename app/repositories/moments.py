def create_moment(cur, user_id, content):
    cur.execute(
        "INSERT INTO moments (user_id,content) VALUES (%s,%s)", (user_id, content)
    )


def update_moment(cur, moment_id, content):
    cur.execute("UPDATE moments SET content=%s WHERE id=%s", (content, moment_id))


def delete_moment(cur, moment_id):
    cur.execute("DELETE FROM moments WHERE id=%s", (moment_id,))


def get_moment(cur, moment_id):
    cur.execute(
        "SELECT m.*,u.username FROM moments m JOIN users u ON m.user_id=u.id WHERE m.id=%s",
        (moment_id,),
    )
    return cur.fetchone()


def list_moments_for_user_and_friends(cur, user_id):
    cur.execute(
        "SELECT m.id,m.content,m.created_at,m.last_update,u.username,m.user_id "
        "FROM moments m JOIN users u ON m.user_id=u.id "
        "WHERE m.user_id=%s OR m.user_id IN (SELECT friend_id FROM friends WHERE user_id=%s) "
        "ORDER BY m.last_update DESC",
        (user_id, user_id),
    )
    return cur.fetchall()


def list_all_moments(cur):
    cur.execute(
        "SELECT m.id,m.content,m.last_update,u.username FROM moments m JOIN users u ON m.user_id=u.id"
    )
    return cur.fetchall()


def list_all_moments_public(cur):
    cur.execute(
        "SELECT m.id,m.content,m.created_at,m.last_update,u.username,m.user_id "
        "FROM moments m JOIN users u ON m.user_id=u.id ORDER BY m.last_update DESC"
    )
    return cur.fetchall()
