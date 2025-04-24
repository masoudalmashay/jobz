from flask import Blueprint, render_template, request
from app.models.job import Job
from app.models.city import City
from app.models.category import Category

from app.models.package import Package
from app.extensions import db, get_user_info
from flask_login import login_required
import os
from dotenv import load_dotenv

load_dotenv()

main = Blueprint("main", __name__)

from flask import request

@main.route("/")
def home():
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category')
    city_id = request.args.get('city')
    page = request.args.get('page', 1, type=int)
    per_page = 2

    query = Job.query

    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if city_id:
        query = query.filter_by(city_id=city_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    raw_jobs = pagination.items

    # fallback to all jobs if filtered list is empty
    if not raw_jobs:
        fallback_query = Job.query.paginate(page=page, per_page=per_page, error_out=False)
        raw_jobs = fallback_query.items
        pagination = fallback_query

    jobs = []
    for job in raw_jobs:
        user_info = get_user_info(job.user_id)
        jobs.append({
            'job': job,
            'user': user_info
        })

    cities = City.query.all()
    categories = Category.query.all()

    return render_template(
        'home.html',
        jobs=jobs,
        pagination=pagination,
        r2_public_url=os.getenv('R2_PUBLIC_URL'),
        cities=cities,
        categories=categories,
        current_search=search,
        current_category=category_id,
        current_city=city_id
    )


@main.route('/prices', methods=["GET", "POST"])
def prices():
    packages = Package.query.all()
    return render_template("prices.html", packages=packages)