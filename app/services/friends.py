from ..db import db_cursor
from ..repositories import friends as friend_repo
from ..repositories import users as user_repo


def list_groups(user_id):
    with db_cursor() as (_, cur):
        return friend_repo.get_group_list(cur, user_id)


def list_friends(user_id):
    with db_cursor() as (_, cur):
        return friend_repo.list_friends(cur, user_id)


def create_group(user_id, name):
    if not name:
        raise ValueError("分组名称不能为空")
    with db_cursor() as (con, cur):
        friend_repo.create_group(cur, user_id, name)
        con.commit()


def send_friend_request(user_id, target_id):
    if target_id == user_id:
        raise ValueError("不能添加自己为好友")
    with db_cursor() as (con, cur):
        if not user_repo.get_by_id(cur, target_id):
            raise ValueError("用户不存在")

        if friend_repo.get_friendship(cur, user_id, target_id):
            raise ValueError("已经是好友")

        existing = friend_repo.get_request(cur, user_id, target_id)
        if existing:
            if existing["status"] == "pending":
                raise ValueError("已发送好友申请")
            friend_repo.reset_request_pending(cur, existing["id"])
            con.commit()
            return

        reverse = friend_repo.get_request(cur, target_id, user_id)
        if reverse and reverse["status"] == "pending":
            raise ValueError("对方已发送申请，请在申请列表处理")

        friend_repo.create_request(cur, user_id, target_id)
        con.commit()


def list_incoming_requests(user_id):
    with db_cursor() as (_, cur):
        return friend_repo.list_requests_for_target(cur, user_id)


def respond_request(user_id, request_id, accept):
    with db_cursor() as (con, cur):
        req = friend_repo.get_request_by_id(cur, request_id)
        if not req or req["target_id"] != user_id:
            raise ValueError("申请不存在")
        if req["status"] != "pending":
            raise ValueError("申请已处理")

        if accept:
            if not friend_repo.get_friendship(cur, user_id, req["requester_id"]):
                friend_repo.add_friendship(cur, user_id, req["requester_id"])
            if not friend_repo.get_friendship(cur, req["requester_id"], user_id):
                friend_repo.add_friendship(cur, req["requester_id"], user_id)
            friend_repo.update_request_status(cur, request_id, "accepted")
        else:
            friend_repo.update_request_status(cur, request_id, "rejected")
        con.commit()


def remove_friend(user_id, friend_id):
    with db_cursor() as (con, cur):
        friend_repo.remove_friendship(cur, user_id, friend_id)
        friend_repo.remove_friendship(cur, friend_id, user_id)
        con.commit()


def assign_group(user_id, friend_id, group_id):
    with db_cursor() as (con, cur):
        if group_id:
            group = friend_repo.get_group_by_id(cur, group_id, user_id)
            if not group:
                raise ValueError("分组不存在")
        friend_repo.assign_group(cur, user_id, friend_id, group_id)
        con.commit()
