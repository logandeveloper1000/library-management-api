# app/blueprints/books/__init__.py
from flask import Blueprint

books_bp = Blueprint('books_bp', __name__)

from . import routes