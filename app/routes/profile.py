from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..services import users as user_service

bp = Blueprint("profile", __name__)


@bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    uid = session["user_id"]
    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        birth = request.form.get("birth") or None
        age = request.form.get("age") or None
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        try:
            if password or confirm:
                if password != confirm:
                    raise ValueError("两次输入的密码不一致")
            user_service.update_profile(uid, name, gender, birth, age, password or None)
            flash("更新成功")
            return redirect(url_for("moments.moments"))
        except Exception as exc:
            flash(f"更新失败: {exc}")
    user = user_service.get_user_profile(uid)
    return render_template("profile.html", user=user)
