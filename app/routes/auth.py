from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..services import users as user_service
from ..services import admins as admin_service

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        try:
            if password != confirm:
                raise ValueError("两次输入的密码不一致")
            user_service.register_user(username, password)
            flash("注册成功")
            return redirect(url_for("auth.login"))
        except Exception as exc:
            flash(f"注册失败: {exc}")
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    role = request.values.get("role", "user")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if role == "admin":
            admin = admin_service.authenticate_admin(username, password)
            if admin:
                session.clear()
                session["admin_id"] = admin["id"]
                session["admin"] = admin["username"]
                return redirect(url_for("admin.admin_panel"))
        else:
            user = user_service.authenticate_user(username, password)
            if user:
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("moments.moments"))
        flash("登录失败")
    return render_template("login.html", role=role)
