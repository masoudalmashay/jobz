from flask import Blueprint, render_template, request
from app.models.job import Job
from app.models.city import City
from app.models.category import Category
from app.models.scraped_job import ScrapedJob

from app.models.package import Package
from app.extensions import db, get_user_info, send_slack_notification, generate_image_template
from flask_login import login_required, current_user
import os
from dotenv import load_dotenv
from app.lib import giphy_trending, mark_jobs
load_dotenv()

main = Blueprint("main", __name__)

from flask import request

@main.route("/")
def home():
    # print(generate_image_template("تقنية معلومات", "بنغازي", "شركة الاختبار", "مهندس برمجيات"))
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category')
    city_id = request.args.get('city')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Job.query.order_by(Job.created_at.desc())
    

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

    marked_jobs = mark_jobs(jobs)

    # --- Scraped jobs ---
    scraped_query = ScrapedJob.query.order_by(ScrapedJob.created_at.desc())
    if search:
        scraped_query = scraped_query.filter(ScrapedJob.title.ilike(f"%{search}%"))
    if city_id:
        city = City.query.get(city_id)
        if city:
            scraped_query = scraped_query.filter(ScrapedJob.city.ilike(f"%{city.name}%"))
    if category_id:
        category = Category.query.get(category_id)
        if category:
            scraped_query = scraped_query.filter(ScrapedJob.category.ilike(f"%{category.name}%"))

    scraped_jobs = scraped_query.limit(20).all()
    scraped_jobs_result = [
        {
            'job': job,
            'user': None,
            'is_new': False,
            'is_hot': False
        }
        for job in scraped_jobs
    ]

    cities = City.query.all()
    categories = Category.query.all()

    giphy = giphy_trending()

    return render_template(
        'home.html',
        jobs=marked_jobs,
        scraped_jobs=scraped_jobs_result,
        pagination=pagination,
        r2_public_url=os.getenv('R2_PUBLIC_URL'),
        cities=cities,
        categories=categories,
        current_search=search,
        current_category=category_id,
        current_city=city_id,
        giphy=giphy
    )


@main.route('/prices', methods=["GET", "POST"])
def prices():
    user_identifier = current_user.email if current_user.is_authenticated else "visitor"
    send_slack_notification(f"Prices page visited by {user_identifier}")

    packages = Package.query.all()
    return render_template("prices.html", packages=packages)