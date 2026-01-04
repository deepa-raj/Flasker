from datetime import datetime, timezone
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

import pymysql
pymysql.install_as_MySQLdb()

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_migrate import Migrate
from wtforms.widgets import TextArea

import itsdangerous
import click
import jinja2
import markupsafe


# Create a Flask Instance
app = Flask(__name__)

# Add Database
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# New MySQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mySQL://username:password@localhost/db_name'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password123@localhost/our_users'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/our_users'
# Secret key!
app.config["SECRET_KEY"] = "my super key that no one is supposed to know"
# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create LoginForm
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!")
                return redirect(url_for("dashboard"))
            else:
                flash("Wrong Password!, Try Again!")
        else:
            flash("That User Doesn't Exist!, Try Again!")

    return render_template("login.html", form=form)


# Create Logout page
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!, Thanks For Stopping By!...")
    return redirect(url_for("login"))


# Create a Dashboard page
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.username = request.form["username"]
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)

        except:
            flash("Error!, Looks like there was a problem")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)

    return render_template("dashboard.html")

# Create a blog post model
class Posts(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(255))
    date_posted: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    slug: Mapped[str] = mapped_column(String(255))


# Create a Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/posts/delete/<int:id>")
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()

        # return a message
        flash("Blog Post Was Deleted")
        # Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

    except:
        # Return an error message
        flash("Whoops! There was a problem deleting post, try again")
        # Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


@app.route("/posts")
def posts():
    # Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for("post", id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("edit_post.html", form=form)

# Add Post Page
@app.route("/add-post", methods=["GET", "POST"])
# @login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        # Clear the form
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a message
        flash("Blog post submitted successfully")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)

# JSON
@app.route("/date")
def get_current_date():
    favorite_pizza = {
        "John": "Pepporoni",
        "Mary": "Cheese",
        "Tim": "Mushroom"
    }
    return favorite_pizza
    # return {"Date": datetime.today()}


# Create Model
class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    favorite_color: Mapped[str] = mapped_column(String(120))
    date_added: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

#     Do some password hashing
    password_hash: Mapped[str] = mapped_column(String(128))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

#     Create A string
    def __repr__(self):
        return "<Name %r>" % self.name


# Deleting the user
@app.route("/delete/<int:id>")
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
    except:
        flash("Whoops!, There was a problem deleting, try again!")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)


# Create a form class
class UserForm(FlaskForm):
    name = StringField( "Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favourite Color")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo("password_hash2", message="Password must match")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Update Database Record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.username = request.form["username"]
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", form=form, name_to_update=name_to_update)

        except:
            flash("Error!, Looks like there was a problem")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id = id)


# Create a PasswordForm Class
class PasswordForm(FlaskForm):
    email = StringField("What is your Email", validators=[DataRequired()])
    password_hash = PasswordField("What is your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What is your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            favorite_color = form.favorite_color.data
            if favorite_color == "":
                favorite_color = None

            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, method="pbkdf2:sha256", salt_length=16)
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, favorite_color=favorite_color, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.favorite_color.data = ""
        form.password_hash.data = ""

        flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)


# Create a route decorator
@app.route("/")
def index():
    first_name = "Deepa"
    stuff = "This is bold text"
    favourite_pizza = ["Pepperoni", "Cheese", "Macrooni", 41]
    return render_template("index.html", first_name=first_name, stuff=stuff, favourite_pizza=favourite_pizza)


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", user_name=name)


# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500


# Create Password Test page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        # clear the form
        form.email.data = ""
        form.password_hash.data = ""

        # Lookup User By Email Address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)

        # flash("Form Submitted Successfully!")
    return render_template("test_pw.html", email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)


# Create Namepage
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()

    # validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form Submitted Successfully!")
    return render_template("name.html", name=name, form=form)


if __name__ == '__main__':
    # with app.app_context():
        # db.create_all()
    app.run(debug=True)