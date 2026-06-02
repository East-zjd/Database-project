from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..services import moments as moment_service
from ..db import db_cursor

bp = Blueprint("moments", __name__)


@bp.route("/moments", methods=["GET", "POST"])
def moments():
    if request.method == "POST":
        if "user_id" not in session:
            flash("请先登录")
            return redirect(url_for("auth.login"))
        content = request.form.get("content", "")
        try:
            moment_service.create_moment(session["user_id"], content)
            flash("发表成功")
        except Exception as exc:
            flash(f"发表失败: {exc}")

    user_id = session.get("user_id")
    rows = moment_service.list_visible_moments(user_id)
    return render_template("moments.html", rows=rows)


@bp.route("/moment/<int:mid>", methods=["GET", "POST"])
def moment_view(mid):
    if request.method == "POST":
        if "user_id" not in session:
            flash("请登录")
            return redirect(url_for("auth.login"))
        content = request.form.get("content", "")
        try:
            moment_service.add_comment(session["user_id"], mid, content)
            flash("评论成功")
        except Exception as exc:
            flash(f"评论失败: {exc}")

    moment, comments = moment_service.get_moment_with_comments(mid)
    return render_template("moment_view.html", moment=moment, comments=comments)


@bp.route("/moment/<int:mid>/edit", methods=["GET", "POST"])
def moment_edit(mid):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        content = request.form.get("content", "")
        try:
            moment_service.update_moment(session["user_id"], mid, content)
            flash("更新成功")
            return redirect(url_for("moments.moment_view", mid=mid))
        except Exception as exc:
            flash(f"更新失败: {exc}")
            return redirect(url_for("moments.moment_view", mid=mid))

    moment, _ = moment_service.get_moment_with_comments(mid)
    return render_template("moment_edit.html", moment=moment)


@bp.route("/moment/<int:mid>/delete", methods=["POST"])
def moment_delete(mid):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    try:
        moment_service.delete_moment(session["user_id"], mid)
        flash("删除成功")
    except Exception as exc:
        flash(f"删除失败: {exc}")
    return redirect(url_for("moments.moments"))


@bp.route("/comment/<int:cid>/delete", methods=["POST"])
def comment_delete(cid):
    if "user_id" not in session and "admin_id" not in session:
        flash("请先登录")
        return redirect(url_for("auth.login"))
    user_id = session.get("user_id")
    is_admin = "admin_id" in session
    # 先获取评论所属的moment_id，以便重定向回动态详情页
    mid = None
    with db_cursor() as (_, cur):
        cur.execute("SELECT moment_id FROM comments WHERE id=%s", (cid,))
        result = cur.fetchone()
        if result:
            mid = result["moment_id"]
    try:
        moment_service.delete_comment(user_id, cid, is_admin)
        flash("评论已删除")
    except Exception as exc:
        flash(f"删除失败: {exc}")
    if mid:
        return redirect(url_for("moments.moment_view", mid=mid))
    return redirect(url_for("moments.moments"))


@bp.route("/comment/<int:cid>/edit", methods=["POST"])
def comment_edit(cid):
    if "user_id" not in session:
        flash("请先登录")
        return redirect(url_for("auth.login"))
    content = request.form.get("content", "")
    # 先获取评论所属的moment_id
    mid = None
    with db_cursor() as (_, cur):
        cur.execute("SELECT moment_id FROM comments WHERE id=%s", (cid,))
        result = cur.fetchone()
        if result:
            mid = result["moment_id"]
    try:
        moment_service.update_comment(session["user_id"], cid, content)
        flash("评论已更新")
    except Exception as exc:
        flash(f"更新失败: {exc}")
    if mid:
        return redirect(url_for("moments.moment_view", mid=mid))
    return redirect(url_for("moments.moments"))
