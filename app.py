from app import create_app
from app.db import init_db, ensure_seed

app = create_app()

with app.app_context():
    init_db()
    ensure_seed()

if __name__ == "__main__":
    app.run(debug=True)
