def add_comment(cur, moment_id, user_id, content):
    cur.execute(
        "INSERT INTO comments (moment_id,user_id,content) VALUES (%s,%s,%s)",
        (moment_id, user_id, content),
    )


def list_comments(cur, moment_id):
    cur.execute(
        "SELECT c.*,u.username FROM comments c JOIN users u ON c.user_id=u.id "
        "WHERE c.moment_id=%s ORDER BY c.created_at",
        (moment_id,),
    )
    return cur.fetchall()


def get_comment(cur, comment_id):
    cur.execute(
        "SELECT c.*, m.user_id as moment_user_id FROM comments c JOIN moments m ON c.moment_id=m.id WHERE c.id=%s",
        (comment_id,),
    )
    return cur.fetchone()


def delete_comment(cur, comment_id):
    cur.execute("DELETE FROM comments WHERE id=%s", (comment_id,))


def update_comment(cur, comment_id, content):
    cur.execute("UPDATE comments SET content=%s WHERE id=%s", (content, comment_id))
