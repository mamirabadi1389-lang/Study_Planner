"""Application configuration."""
import os
import sys
from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent.parent

# PyInstaller sets sys.frozen in the packaged build.
# Nuitka sets __compiled__ in every module; packagers set sys.frozen.
FROZEN: bool = (
    bool(getattr(sys, "frozen", False)) or "__compiled__" in globals()
)

if FROZEN:
    # Installed build: the program folder is read-only, so user data
    # lives in the per-user application data directory.
    DATA_DIR: Path = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Planner"
else:
    DATA_DIR = BASE_DIR / "data"

DATABASE_PATH: Path = DATA_DIR / "planner.db"
SECRET_KEY: str = "local-only-change-me"

THEMES: tuple[str, ...] = ("neon", "ocean", "sunset", "forest", "light")
DEFAULT_SETTINGS: dict[str, str] = {
    "theme": "neon",
    "name": "",
    "daily_goal": "5",
    "focus_minutes": "25",
}