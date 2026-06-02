from werkzeug.security import check_password_hash, generate_password_hash
from ..db import db_cursor
from ..repositories import admins as admin_repo
from ..repositories import moments as moment_repo
from ..repositories import users as user_repo


def authenticate_admin(username, password):
    with db_cursor() as (_, cur):
        admin = admin_repo.get_by_username(cur, username)
        if admin and check_password_hash(admin["password"], password):
            return admin
        return None


def get_admin_profile(admin_id):
    with db_cursor() as (_, cur):
        return admin_repo.get_by_id(cur, admin_id)


def update_admin_profile(admin_id, name, password):
    with db_cursor() as (con, cur):
        pw_hash = generate_password_hash(password) if password else None
        admin_repo.update_profile(cur, admin_id, name, pw_hash)
        con.commit()


def list_all_moments():
    with db_cursor() as (_, cur):
        return moment_repo.list_all_moments(cur)


def list_users():
    with db_cursor() as (_, cur):
        return user_repo.list_users(cur)


def delete_moment(moment_id):
    with db_cursor() as (con, cur):
        moment_repo.delete_moment(cur, moment_id)
        con.commit()


def delete_user(user_id):
    with db_cursor() as (con, cur):
        cur.execute("START TRANSACTION")
        user_repo.delete_by_id(cur, user_id)
        con.commit()
