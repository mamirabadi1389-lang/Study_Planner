"""Page routes."""
from flask import Blueprint, render_template

from ..services import settings

bp = Blueprint("pages", __name__)


@bp.get("/")
def index() -> str:
    """Render the app shell with the saved theme."""
    return render_template("index.html", theme=settings.load()["theme"])