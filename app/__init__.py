from pathlib import Path
from flask import Flask


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    try:
        from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    except Exception:
        DB_HOST = "localhost"
        DB_PORT = 3306
        DB_USER = "root"
        DB_PASSWORD = ""
        DB_NAME = "social_db"

    app.config.update(
        DB_HOST=DB_HOST,
        DB_PORT=DB_PORT,
        DB_USER=DB_USER,
        DB_PASSWORD=DB_PASSWORD,
        DB_NAME=DB_NAME,
        BASE_DIR=Path(__file__).resolve().parents[1],
        SECRET_KEY=app.config.get("SECRET_KEY") or "dev-secret",
    )

    from .routes.common import bp as common_bp
    from .routes.auth import bp as auth_bp
    from .routes.profile import bp as profile_bp
    from .routes.moments import bp as moments_bp
    from .routes.friends import bp as friends_bp
    from .routes.admin import bp as admin_bp

    app.register_blueprint(common_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(moments_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(admin_bp)

    return app
