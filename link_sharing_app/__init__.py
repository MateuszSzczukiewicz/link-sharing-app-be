import os
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv
from flask import Flask

from . import auth, db, links, users

load_dotenv()


def create_app(test_config: Optional[Dict[str, bool | str]] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    secret_key = os.getenv("SECRET_KEY")

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DATABASE=f"file:{
            os.path.join(
                app.instance_path,
                'link_sharing_app.sqlite')}?mode=rwc",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(links.bp)

    @app.route("/")
    def health_check() -> Tuple[Dict[str, str], int]:
        return {"status": "ok"}, 200

    return app
