"""
Blog Application
Description: A full-stack Flask web application utilizing SQLite for database management,
WTForms for secure data entry, and CKEditor for rich-text article formatting.
"""

import os
import bleach
import smtplib
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, TextAreaField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditor, CKEditorField

# Initialize environment variables
load_dotenv()

# Application Configuration
my_email = os.getenv("MY_EMAIL")
password = os.getenv("MY_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = "smtp.gmail.com"
PORT = 465

# Initialize Flask and Extensions
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "8BYkEfBA6O6donzWlSihBXox7C0sKR6b")
Bootstrap5(app)
ckeditor = CKEditor(app)


# ---------------------------------------------------------------------------
# CONTEXT PROCESSORS
# ---------------------------------------------------------------------------
@app.context_processor
def inject_now():
    """Automatically injects the current year into all Jinja templates."""
    return {'current_year': datetime.now().year}


# ---------------------------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class BlogPost(db.Model):
    """Database model representing a single blog post."""
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# WTFORMS CONFIGURATION
# ---------------------------------------------------------------------------
class BlogPostForm(FlaskForm):
    """Form class for creating and editing blog posts (Uses CKEditor)."""
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    img_url = URLField("Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Body", validators=[DataRequired()])
    submit = SubmitField("Submit", render_kw={"class": "btn btn-primary text-uppercase"})


class ContactForm(FlaskForm):
    """Form class for the contact page (Uses Standard Text Area)."""
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send", render_kw={"class": "btn btn-primary text-uppercase"})


# ---------------------------------------------------------------------------
# APPLICATION ROUTES
# ---------------------------------------------------------------------------

@app.route('/')
def home():
    all_post = db.session.scalars(db.select(BlogPost))
    posts = [entry for entry in all_post]
    return render_template("index.html", all_posts=posts)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    requested_post = db.session.get(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        msg = EmailMessage()
        msg["Subject"] = f"New Message from {form.name.data} (Portfolio Contact)"
        msg["From"] = my_email
        msg["To"] = receiver_email

        msg.set_content(f"""\
Name: {form.name.data}
Email: {form.email.data}
Phone: {form.phone_number.data}

Message: 
{form.message.data}
""")

        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, PORT) as connection:
                connection.login(user=my_email, password=password)
                connection.send_message(msg)
            return render_template('contact.html', form=form, success="success")

        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('contact.html', form=form, success="error")

    return render_template('contact.html', form=form)


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    form = BlogPostForm()

    if form.validate_on_submit():
        # Security: Bleach Bouncer
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'br']
        clean_body = bleach.clean(form.body.data, tags=allowed_tags)

        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=clean_body,
            author=form.author.data,
            img_url=form.img_url.data,
            date=datetime.now().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)

    edit_form = BlogPostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )

    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data

        # Security: Sanitize edited content
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'br']
        post.body = bleach.clean(edit_form.body.data, tags=allowed_tags)

        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    # Passes is_edit and post_id for the Cancel routing logic
    return render_template("make-post.html", form=edit_form, is_edit=True, post_id=post.id)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=5003)