"""
Blog Application Orchestrator
Core system coordinating configurations, table schemas, relationships, and endpoints.
"""
import os
import smtplib
import bleach
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

# --- Modular Architecture Imports ---
from extensions import db
from models import User, BlogPost, Comment
from admin import admin_bp
from forms import CreatePostForm, ContactForm, RegisterForm, LoginForm, CommentForm
from utils import gravatar_url, is_safe_url

load_dotenv()

# --- Configuration ---
MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = "smtp.gmail.com"
PORT = 465

app = Flask(__name__)

# Force a fast failure if the secret key is missing in production to prevent insecure fallback
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
if not app.config['SECRET_KEY']:
    raise ValueError("Critical Error: No SECRET_KEY set for Flask application. Check environment variables.")

# Dynamically route the database connection
# Defaults to a local SQLite file for development if no cloud DB_URL is provided
db_url = os.environ.get("DB_URL", "sqlite:///posts.db")

# SQLAlchemy 1.4+ strictly requires the 'postgresql://' scheme.
# This safely patches legacy 'postgres://' connection strings provided by cloud hosts like Supabase or Render.
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url


# Inject global utilities into the Jinja context
app.jinja_env.globals.update(gravatar_url=gravatar_url)

# --- Bind Extensions ---
db.init_app(app)
ckeditor = CKEditor(app)
Bootstrap5(app)

# Register Sub-Modules
app.register_blueprint(admin_bp)

# --- Configure Security & Sessions ---
SALT_LENGTH = 20

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "You need to login to view this page."
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(user_id):
    """Reconstructs the user session from the active database."""
    return db.session.get(User, int(user_id))

@app.errorhandler(403)
def forbidden_route(e):
    """Handles unauthorized access attempts gracefully."""
    return render_template("403.html"), 403

@app.context_processor
def inject_now():
    """Provides dynamic date rendering for global templates."""
    return {'current_year': datetime.now().year}


# =====================================================================
# AUTHENTICATION ENDPOINTS
# =====================================================================

@app.route('/register', methods=["GET", "POST"])
def register():
    """Handles the ingestion and secure hashing of new user credentials."""
    register_form = RegisterForm()
    next_url = request.args.get('next')

    if request.method == "GET":
        saved_email = session.pop('prefill_email', None)
        if saved_email:
            register_form.email.data = saved_email

    if register_form.validate_on_submit():
        existing_user = db.session.execute(
            db.select(User).where(or_(User.email == register_form.email.data, User.name == register_form.username.data))
        ).scalar()

        if existing_user:
            if existing_user.email == register_form.email.data:
                session['prefill_email'] = register_form.email.data
                flash("You've already signed up with that email. Log in instead!", "danger")
                return redirect(url_for('login', next=next_url))
            else:
                flash("That username is already taken. Please choose a different one.", "warning")
                return render_template("register.html", form=register_form, next=next_url)

        hashed_password = generate_password_hash(register_form.password.data, method='scrypt', salt_length=SALT_LENGTH)
        new_user = User(email=register_form.email.data, name=register_form.username.data, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        if next_url and not is_safe_url(next_url):
            response = redirect(url_for('get_all_posts'))
            response.status_code = 400
            return response
        return redirect(next_url or url_for('get_all_posts'))

    return render_template("register.html", form=register_form, next=next_url)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Authenticates existing users and initializes their session state."""
    login_form = LoginForm()
    next_url = request.args.get('next')

    if request.method == "GET":
        saved_email = session.pop('prefill_email', None)
        if saved_email:
            login_form.email_or_username.data = saved_email

    if login_form.validate_on_submit():
        user_input = login_form.email_or_username.data
        user_password = login_form.password.data
        user = db.session.execute(
            db.select(User).where(or_(User.email == user_input, User.name == user_input))).scalar()

        # Security Update: Unify the failure conditions to prevent enumeration
        if not user or not check_password_hash(user.password, user_password):
            flash("Username or password incorrect. Please try again.", "danger")
            return render_template("login.html", form=login_form, next=next_url)

        # Success condition remains the same
        else:
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')

            if next_url and not is_safe_url(next_url):
                response = redirect(url_for('get_all_posts'))
                response.status_code = 400
                return response
            return redirect(next_url or url_for('get_all_posts'))

    return render_template("login.html", form=login_form, next=next_url)

@app.route('/logout')
@login_required
def logout():
    """Terminates the active user session."""
    logout_user()
    flash("You have been successfully logged out.", "primary")
    return redirect(url_for('get_all_posts'))


# =====================================================================
# CORE APPLICATION ENDPOINTS
# =====================================================================

@app.route('/')
def get_all_posts():
    """Retrieves and renders the primary data feed."""
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    """Renders individual data models and handles child entity ingestion."""
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.", "danger")
            return redirect(url_for("login", next=url_for('show_post', post_id=post_id)))

        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'p', 'br']
        clean_comment = bleach.clean(comment_form.comment.data, tags=allowed_tags)

        new_comment = Comment(text=clean_comment, comment_author=current_user, parent_post=requested_post)
        db.session.add(new_comment)
        db.session.commit()

        flash("Comment posted successfully!", "success")
        return redirect(url_for('show_post', post_id=requested_post.id))

    return render_template("post.html", post=requested_post, form=comment_form)

@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    """Creates new parent entities mapped to the current authenticated user."""
    form = CreatePostForm()

    if form.validate_on_submit():
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'br']
        clean_body = bleach.clean(form.body.data, tags=allowed_tags)

        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=clean_body,
            img_url=form.img_url.data,
            author=current_user,
            date=datetime.now().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form)

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    """Handles entity modification with strict Role-Based Access Control."""
    post = db.get_or_404(BlogPost, post_id)

    if current_user.id != post.author_id and current_user.id != 1:
        flash("Unauthorized access attempt.", "danger")
        return render_template("403.html"), 403

    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )

    if edit_form.validate_on_submit():
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'br']
        clean_body = bleach.clean(edit_form.body.data, tags=allowed_tags)

        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = clean_body

        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True)

@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    """Triggers the destructive cascade for parent entities and associated children."""
    post_to_delete = db.get_or_404(BlogPost, post_id)

    if current_user.id != post_to_delete.author_id and not current_user.is_admin and current_user.id != 1:
        flash("Unauthorized access attempt.", "danger")
        return render_template("403.html"), 403

    db.session.delete(post_to_delete)
    db.session.commit()
    flash("Post deleted successfully.", "success")
    return redirect(url_for('get_all_posts'))


@app.route("/delete-comment/<int:comment_id>/<int:post_id>")
def delete_comment(comment_id, post_id):
    """Allows comment authors, moderators, and super admins to delete comments."""
    comment_to_delete = db.get_or_404(Comment, comment_id)

    # Permission Check: Author OR Moderator (is_admin) OR Super Admin (ID 1)
    if current_user.is_authenticated and (
            current_user.id == comment_to_delete.comment_author.id or current_user.is_admin or current_user.id == 1):
        db.session.delete(comment_to_delete)
        db.session.commit()
        flash("Comment deleted successfully.", "success")
    else:
        flash("You do not have permission to delete this comment.", "danger")

    return redirect(url_for('show_post', post_id=post_id))


# =====================================================================
# STATIC & COMMUNICATION ENDPOINTS
# =====================================================================

@app.route("/about")
def about():
    """Renders the static portfolio/information page."""
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Handles external communications via secure SMTP relay."""
    form = ContactForm()

    if request.method == "GET" and current_user.is_authenticated:
        form.email.data = current_user.email

    if form.validate_on_submit():
        msg = EmailMessage()
        msg["Subject"] = f"New Message from {form.name.data} (Portfolio Contact)"
        msg["From"] = MY_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg.set_content(f"Name: {form.name.data}\nEmail: {form.email.data}\nPhone: {form.phone_number.data}\n\nMessage:\n{form.message.data}")

        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, PORT) as connection:
                connection.login(user=MY_EMAIL, password=MY_PASSWORD)
                connection.send_message(msg)
            return render_template("contact.html", form=form, success="success")
        except Exception as e:
            print(f"SMTP Error: {e}")
            return render_template("contact.html", form=form, success="error")

    return render_template("contact.html", form=form)

if __name__ == "__main__":
    app.run(debug=True, port=5000)