from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"

TEMPLATES = ROOT / "app" / "templates"
STATIC_SRC = ROOT / "app" / "static"
STATIC_OUT = BUILD / "static_min"

ICON = STATIC_SRC / "img" / "logo.ico"


def _prepare_static(minify: bool) -> None:
    """Copy static files and optionally minify JS/CSS."""

    BUILD.mkdir(exist_ok=True)

    if STATIC_OUT.exists():
        shutil.rmtree(STATIC_OUT)

    shutil.copytree(STATIC_SRC, STATIC_OUT)

    if not minify:
        return

    try:
        import rcssmin
        import rjsmin
    except ImportError:
        print("rjsmin/rcssmin not installed: static files left unminified")
        return

    # Minify JavaScript files
    for path in STATIC_OUT.rglob("*.js"):
        path.write_text(
            rjsmin.jsmin(path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )

    # Minify CSS files
    for path in STATIC_OUT.rglob("*.css"):
        path.write_text(
            rcssmin.cssmin(path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )


def _nuitka(debug: bool, fast: bool) -> int:
    """Run Nuitka for the Windows pywebview application."""

    console = "force" if debug else "disable"

    jobs = (os.cpu_count() or 2) if fast else 2

    cmd = [
        sys.executable,
        "-m",
        "nuitka",

        # Build mode
        "--standalone",
        "--assume-yes-for-downloads",

        # Performance / resources
        f"--jobs={jobs}",
        f"--windows-console-mode={console}",

        # Application icon
        f"--windows-icon-from-ico={ICON}",

        # Output
        f"--output-dir={BUILD}",
        "--output-filename=Planner.exe",

        # HTML templates
        f"--include-data-dir={TEMPLATES}=app/templates",

        # Static files
        f"--include-data-dir={STATIC_OUT}=app/static",

        # pywebview
        #
        # IMPORTANT:
        # Do NOT use --include-package=webview here.
        # It conflicts with Nuitka's pywebview plugin and can
        # cause:
        # "Conflict between user and plugin decision for module
        # 'webview.platforms.android'."
        #
        "--enable-plugin=pywebview",

        # Prevent unnecessary imports
        "--nofollow-import-to=tkinter",
        "--nofollow-import-to=test",
        "--nofollow-import-to=pydoc_data",

        # Reduce memory usage during compilation
        # when --fast is not selected
    ]

    if not fast:
        cmd.append("--low-memory")

    # Main entry point must be the LAST argument.
    cmd.append(str(ROOT / "run.py"))

    print("\nRunning Nuitka:\n")
    print(" ".join(f'"{x}"' if " " in x else x for x in cmd))
    print()

    return subprocess.call(cmd, cwd=ROOT)


def main() -> None:
    args = set(sys.argv[1:])

    # Prepare static files
    _prepare_static(
        minify="--no-minify" not in args
    )

    # Build application
    code = _nuitka(
        debug="--debug" in args,
        fast="--fast" in args,
    )

    if code == 0:
        print("\n========================================")
        print("Build completed successfully!")
        print(f"Planner.exe: {BUILD / 'run.dist' / 'Planner.exe'}")
        print("========================================\n")

    else:
        print("\n========================================")
        print("Nuitka build failed.")
        print("========================================\n")

    sys.exit(code)


if __name__ == "__main__":
    main()