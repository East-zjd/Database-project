from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..services import admins as admin_service

bp = Blueprint("admin", __name__)


@bp.route("/admin/login", methods=["GET"])
def admin_login():
    return redirect(url_for("auth.login", role="admin"))


@bp.route("/admin/profile", methods=["GET", "POST"])
def admin_profile():
    if "admin_id" not in session:
        return redirect(url_for("admin.admin_login"))
    aid = session["admin_id"]
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        try:
            if password or confirm:
                if password != confirm:
                    raise ValueError("两次输入的密码不一致")
            admin_service.update_admin_profile(aid, name, password)
            flash("更新成功")
            return redirect(url_for("admin.admin_panel"))
        except Exception as exc:
            flash(f"更新失败: {exc}")
    admin = admin_service.get_admin_profile(aid)
    return render_template("admin_profile.html", admin=admin)


@bp.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if "admin_id" not in session:
        return redirect(url_for("admin.admin_login"))
    if request.method == "POST":
        uid = request.form.get("delete_user")
        if uid:
            try:
                admin_service.delete_user(uid)
                flash("用户及相关数据已删除")
            except Exception as exc:
                flash(f"删除失败: {exc}")

    moments = admin_service.list_all_moments()
    users = admin_service.list_users()
    return render_template("admin_panel.html", moments=moments, users=users)


@bp.route("/admin/moment/delete/<int:mid>", methods=["POST"])
def admin_delete_moment(mid):
    if "admin_id" not in session:
        return redirect(url_for("admin.admin_login"))
    try:
        admin_service.delete_moment(mid)
        flash("动态已删除")
    except Exception as exc:
        flash(f"删除失败: {exc}")
    return redirect(url_for("admin.admin_panel"))


@bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin", None)
    flash("管理员已登出")
    return redirect(url_for("common.index"))
