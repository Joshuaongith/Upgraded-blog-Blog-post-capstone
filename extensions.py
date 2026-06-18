"""
Database Extension Module
Isolates the SQLAlchemy instance to prevent circular dependencies across Blueprints.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy object without binding it to the Flask app yet.
db = SQLAlchemy()