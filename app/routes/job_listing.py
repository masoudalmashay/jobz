
from flask import Blueprint, request, session, render_template, url_for

from flask_login import login_required, current_user

job_listing = Blueprint("job_listing", __name__)



@job_listing.before_request
def redirect_if_not_authenticated():
    if request.endpoint == 'job_listing.add' and not current_user.is_authenticated:
        session['next'] = request.url


@job_listing.route('/')
@login_required
def add():
    print(request.endpoint)
    return render_template("job_listing/add.html")