from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..services import friends as friend_service
from ..services import users as user_service

bp = Blueprint("friends", __name__)


@bp.route("/friends", methods=["GET", "POST"])
def friends():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    uid = session["user_id"]
    search_results = []
    if request.method == "POST":
        action = request.form.get("action")
        if action == "search":
            keyword = request.form.get("username", "")
            search_results = user_service.search_users(keyword)
        elif action == "add":
            try:
                target = int(request.form.get("target_id"))
                friend_service.send_friend_request(uid, target)
                flash("已发送好友申请")
            except Exception as exc:
                flash(f"添加好友失败: {exc}")
        elif action == "create_group":
            try:
                name = request.form.get("group_name", "")
                friend_service.create_group(uid, name)
                flash("分组创建成功")
            except Exception as exc:
                flash(f"创建分组失败: {exc}")
        elif action == "accept_request":
            try:
                req_id = int(request.form.get("request_id"))
                friend_service.respond_request(uid, req_id, True)
                flash("已同意好友申请")
            except Exception as exc:
                flash(f"处理申请失败: {exc}")
        elif action == "reject_request":
            try:
                req_id = int(request.form.get("request_id"))
                friend_service.respond_request(uid, req_id, False)
                flash("已拒绝好友申请")
            except Exception as exc:
                flash(f"处理申请失败: {exc}")

    groups = friend_service.list_groups(uid)
    friends_list = friend_service.list_friends(uid)
    incoming_requests = friend_service.list_incoming_requests(uid)
    return render_template(
        "friends.html",
        search_results=search_results,
        friends_list=friends_list,
        groups=groups,
        incoming_requests=incoming_requests,
    )


@bp.route("/friend/remove/<int:fid>", methods=["POST"])
def friend_remove(fid):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    try:
        friend_service.remove_friend(session["user_id"], fid)
        flash("已移除好友")
    except Exception as exc:
        flash(f"移除失败: {exc}")
    return redirect(url_for("friends.friends"))


@bp.route("/friend/assign/<int:fid>", methods=["POST"])
def friend_assign(fid):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    group_id = request.form.get("group_id") or None
    try:
        friend_service.assign_group(session["user_id"], fid, group_id)
        flash("分组分配成功")
    except Exception as exc:
        flash(f"分配失败: {exc}")
    return redirect(url_for("friends.friends"))
