def get_group_list(cur, user_id):
    cur.execute("SELECT id,name FROM friend_groups WHERE user_id=%s", (user_id,))
    return cur.fetchall()


def create_group(cur, user_id, name):
    cur.execute(
        "INSERT INTO friend_groups (user_id,name) VALUES (%s,%s)", (user_id, name)
    )


def get_group_by_id(cur, group_id, user_id):
    cur.execute(
        "SELECT id FROM friend_groups WHERE id=%s AND user_id=%s",
        (group_id, user_id),
    )
    return cur.fetchone()


def get_friendship(cur, user_id, friend_id):
    cur.execute(
        "SELECT id FROM friends WHERE user_id=%s AND friend_id=%s",
        (user_id, friend_id),
    )
    return cur.fetchone()


def add_friendship(cur, user_id, friend_id):
    cur.execute(
        "INSERT INTO friends (user_id,friend_id) VALUES (%s,%s)",
        (user_id, friend_id),
    )


def remove_friendship(cur, user_id, friend_id):
    cur.execute(
        "DELETE FROM friends WHERE user_id=%s AND friend_id=%s",
        (user_id, friend_id),
    )


def assign_group(cur, user_id, friend_id, group_id):
    cur.execute(
        "UPDATE friends SET group_id=%s WHERE user_id=%s AND friend_id=%s",
        (group_id, user_id, friend_id),
    )


def list_friends(cur, user_id):
    cur.execute(
        "SELECT f.id as fid,u.id as uid,u.username,fg.name as group_name,fg.id as group_id "
        "FROM friends f JOIN users u ON f.friend_id=u.id "
        "LEFT JOIN friend_groups fg ON f.group_id=fg.id "
        "WHERE f.user_id=%s",
        (user_id,),
    )
    return cur.fetchall()


def get_request(cur, requester_id, target_id):
    cur.execute(
        "SELECT * FROM friend_requests WHERE requester_id=%s AND target_id=%s",
        (requester_id, target_id),
    )
    return cur.fetchone()


def get_request_by_id(cur, request_id):
    cur.execute("SELECT * FROM friend_requests WHERE id=%s", (request_id,))
    return cur.fetchone()


def create_request(cur, requester_id, target_id):
    cur.execute(
        "INSERT INTO friend_requests (requester_id,target_id) VALUES (%s,%s)",
        (requester_id, target_id),
    )


def update_request_status(cur, request_id, status):
    cur.execute(
        "UPDATE friend_requests SET status=%s WHERE id=%s", (status, request_id)
    )


def reset_request_pending(cur, request_id):
    cur.execute(
        "UPDATE friend_requests SET status='pending', created_at=CURRENT_TIMESTAMP WHERE id=%s",
        (request_id,),
    )


def list_requests_for_target(cur, target_id):
    cur.execute(
        "SELECT fr.id,fr.requester_id,fr.created_at,u.username,u.name "
        "FROM friend_requests fr JOIN users u ON fr.requester_id=u.id "
        "WHERE fr.target_id=%s AND fr.status='pending' ORDER BY fr.created_at DESC",
        (target_id,),
    )
    return cur.fetchall()
