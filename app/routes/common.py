from flask import Blueprint, render_template, session, redirect, url_for, flash

bp = Blueprint("common", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("已登出")
    return redirect(url_for("common.index"))
