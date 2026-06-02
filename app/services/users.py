from werkzeug.security import generate_password_hash, check_password_hash
from ..db import db_cursor
from ..repositories import users as user_repo


def register_user(username, password):
    with db_cursor() as (con, cur):
        existing = user_repo.get_by_username(cur, username)
        if existing:
            raise ValueError("用户名已存在")
        pw = generate_password_hash(password)
        user_repo.create_user(cur, username, pw)
        con.commit()


def authenticate_user(username, password):
    with db_cursor() as (_, cur):
        user = user_repo.get_by_username(cur, username)
        if user and check_password_hash(user["password"], password):
            return user
        return None


def get_user_profile(user_id):
    with db_cursor() as (_, cur):
        return user_repo.get_by_id(cur, user_id)


def update_profile(user_id, name, gender, birthdate, age, password=None):
    with db_cursor() as (con, cur):
        user_repo.update_profile(cur, user_id, name, gender, birthdate, age)
        if password:
            pw_hash = generate_password_hash(password)
            user_repo.update_password(cur, user_id, pw_hash)
        con.commit()


def search_users(keyword):
    with db_cursor() as (_, cur):
        return user_repo.search_by_username(cur, keyword)
