from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


import itsdangerous
import click
import jinja2
import markupsafe


# Create a Flask Instance
app = Flask(__name__)


# Create a route decorator
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/user/<name>")
def user(name):
    return f"<h1>Hello {name}!</h1>"




if __name__ == '__main__':
    app.run(debug=True)