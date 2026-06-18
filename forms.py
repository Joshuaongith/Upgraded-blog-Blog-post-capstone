"""
Forms Configuration Module
Defines secure data entry models using WTForms and Flask-CKEditor fields.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired, URL, Email, Length, Regexp, EqualTo
from flask_ckeditor import CKEditorField

class CreatePostForm(FlaskForm):
    """Form used by authors and administrators to publish or edit a blog article."""
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class ContactForm(FlaskForm):
    """Form enabling asynchronous user outreach processing via email transmission."""
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email Address", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")

class RegisterForm(FlaskForm):
    """Form establishing secure customer credentials containing explicit validation rules."""
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=8),
        Regexp(
            r'^(?=.*[A-Z])(?=.*[\W_]).+$',
            message="Password must contain at least one capital letter and one symbol."
        )
    ])
    renter_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    """Unified entry credential interface validating multi-column user identities."""
    email_or_username = StringField("Email or Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")

class CommentForm(FlaskForm):
    """Rich text comment collection system utilizing integrated text layout scripts."""
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")