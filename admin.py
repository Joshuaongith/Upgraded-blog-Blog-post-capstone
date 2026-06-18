"""
Super Administration Blueprint Module
Controls access restriction parameters, permission hierarchies, and tier modifications.
"""
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from functools import wraps
from extensions import db
from models import User, BlogPost

admin_bp = Blueprint('admin_bp', __name__)

def super_admin_only(f):
    """
    Security wrapper restricting access to explicit Super Admin (ID 1).
    Moderators with is_admin=True do not have access to the Admin Portal.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            flash("You do not have administrative privileges.", "danger")
            return render_template("403.html"), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/admin/portal")
@login_required
@super_admin_only
def portal():
    """Compiles dashboard visualization tables tracking global environment assets."""
    users = db.session.execute(db.select(User)).scalars().all()
    all_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("admin_portal.html", users=users, all_posts=all_posts)

@admin_bp.route("/admin/toggle/<int:user_id>")
@login_required
@super_admin_only
def toggle_admin(user_id):
    """
    Flips access booleans symmetrically between standard accounts and administrators.
    The Principal Administrator (ID 1) is protected from modification.
    """
    if user_id == 1:
        flash("Modifying the principal administrator node is prohibited.", "danger")
        return redirect(url_for('admin_bp.portal'))

    user = db.get_or_404(User, user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Updated status permissions for: {user.name}.", "success")
    return redirect(url_for('admin_bp.portal'))

@admin_bp.route("/admin/delete/<int:user_id>")
@login_required
@super_admin_only
def delete_user(user_id):
    """
    Removes targeted user records completely from relational architecture.
    The Principal Administrator (ID 1) is protected from deletion.
    """
    if user_id == 1:
        flash("Dropping the principal system administrator node is blocked.", "danger")
        return redirect(url_for('admin_bp.portal'))

    user_to_delete = db.get_or_404(User, user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f"Permanently dropped profile: {user_to_delete.name}.", "success")
    return redirect(url_for('admin_bp.portal'))