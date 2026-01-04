from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
# from flask_wtf.file import FileField

# Create a Search Form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create LoginForm
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Post form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # content = TextAreaField("Content", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a form class
class UserForm(FlaskForm):
    name = StringField( "Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favourite Color")
    about_author = TextAreaField("About Author")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo("password_hash2", message="Password must match")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField("Submit")


# Create a PasswordForm Class
class PasswordForm(FlaskForm):
    email = StringField("What is your Email", validators=[DataRequired()])
    password_hash = PasswordField("What is your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a NamerForm Class
class NamerForm(FlaskForm):
    name = StringField("What is your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

