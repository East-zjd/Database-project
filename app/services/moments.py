from ..db import db_cursor
from ..repositories import moments as moment_repo
from ..repositories import comments as comment_repo


def list_visible_moments(user_id=None):
    with db_cursor() as (_, cur):
        if user_id:
            return moment_repo.list_moments_for_user_and_friends(cur, user_id)
        return moment_repo.list_all_moments_public(cur)


def create_moment(user_id, content):
    if not content or len(content) > 500:
        raise ValueError("内容为空或超出500字限制")
    with db_cursor() as (con, cur):
        moment_repo.create_moment(cur, user_id, content)
        con.commit()


def update_moment(user_id, moment_id, content):
    if not content or len(content) > 500:
        raise ValueError("内容为空或超出500字限制")
    with db_cursor() as (con, cur):
        moment = moment_repo.get_moment(cur, moment_id)
        if not moment:
            raise ValueError("动态不存在")
        if moment["user_id"] != user_id:
            raise ValueError("无权编辑")
        moment_repo.update_moment(cur, moment_id, content)
        con.commit()


def delete_moment(user_id, moment_id):
    with db_cursor() as (con, cur):
        moment = moment_repo.get_moment(cur, moment_id)
        if not moment:
            raise ValueError("动态不存在")
        if moment["user_id"] != user_id:
            raise ValueError("无权删除")
        moment_repo.delete_moment(cur, moment_id)
        con.commit()


def get_moment_with_comments(moment_id):
    with db_cursor() as (_, cur):
        moment = moment_repo.get_moment(cur, moment_id)
        comments = comment_repo.list_comments(cur, moment_id)
    return moment, comments


def add_comment(user_id, moment_id, content):
    if not content:
        raise ValueError("评论不能为空")
    with db_cursor() as (con, cur):
        comment_repo.add_comment(cur, moment_id, user_id, content)
        con.commit()


def delete_comment(user_id, comment_id, is_admin=False):
    with db_cursor() as (con, cur):
        comment = comment_repo.get_comment(cur, comment_id)
        if not comment:
            raise ValueError("评论不存在")
        if not is_admin and comment["user_id"] != user_id and comment["moment_user_id"] != user_id:
            raise ValueError("无权删除此评论")
        comment_repo.delete_comment(cur, comment_id)
        con.commit()


def update_comment(user_id, comment_id, content):
    if not content:
        raise ValueError("评论不能为空")
    with db_cursor() as (con, cur):
        comment = comment_repo.get_comment(cur, comment_id)
        if not comment:
            raise ValueError("评论不存在")
        if comment["user_id"] != user_id:
            raise ValueError("无权编辑此评论")
        comment_repo.update_comment(cur, comment_id, content)
        con.commit()
