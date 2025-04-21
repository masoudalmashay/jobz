
from flask import Blueprint, redirect, url_for, render_template


profile = Blueprint("profile", __name__)


@profile.route('/')
def index():
    return render_template('profile/index.html')