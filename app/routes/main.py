from flask import Blueprint, render_template
from app.models.job import Job
from app.extensions import db

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template('home.html')


@main.route("/about")
def about():
    return render_template('about.html')

@main.route("/prices")
def prices():
    return render_template('prices.html')




@main.route('/create')
def create():
    job = Job(title="test", description="this is a test")
    db.session.add(job)
    db.session.commit()

    return "done"


@main.route('/all')
def all():
    return f"jobs: {len(Job.query.all())}"
