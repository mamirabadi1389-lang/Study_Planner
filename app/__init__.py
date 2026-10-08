"""Application factory."""
from flask import Flask

from . import config, database


def create_app() -> Flask:
    """Build and configure the Flask app."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    database.init_app(app)

    from .routes import api, pages, stats

    app.register_blueprint(pages.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(stats.bp)
    return app