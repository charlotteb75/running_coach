from pathlib import Path

from flask import Blueprint, render_template, send_from_directory

docs_bp = Blueprint("docs", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@docs_bp.get("/openapi.yaml")
def get_openapi():
    return send_from_directory(
        PROJECT_ROOT,
        "openapi.yaml",
        mimetype="application/yaml",
    )


@docs_bp.get("/docs")
def get_docs():
    return render_template("docs.html")