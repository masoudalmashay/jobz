
from flask import Blueprint, request, session, render_template, url_for, flash, redirect

from flask_login import login_required, current_user

from app.forms.job_form import JobForm

from app.models.order import Order
from app.models.job import Job
from app.models.scraped_job import ScrapedJob
from app.models.category import Category
from app.models.city import City
from app.models.social_post import SocialPost

from datetime import datetime, timedelta

from app.extensions import db, get_user_info, send_slack_notification, post_to_social_media
from app.lib import can_post_today

from slugify import slugify
import uuid

import os

from dotenv import load_dotenv

load_dotenv()

job_listing = Blueprint("job_listing", __name__)



@job_listing.before_request
def redirect_if_not_authenticated():
    if request.endpoint == 'job_listing.add' and not current_user.is_authenticated:
        session['next'] = request.url


@job_listing.route('/', methods=["GET", "POST"])
@login_required
def add():
    form = JobForm()
    form.set_choices()

    valid_orders = Order.query.filter(
        Order.user_id == current_user.id,
        Order.posts_used < Order.post_limit
    ).order_by(Order.purchased_at.asc()).all()

    credits = sum([order.post_limit - order.posts_used for order in valid_orders])


    if form.validate_on_submit():
        # Get the oldest valid order with remaining posts
        valid_order = Order.query.filter(
            Order.user_id == current_user.id,
            Order.posts_used < Order.post_limit
        ).order_by(Order.purchased_at.asc()).first()

        if not valid_order:
            flash("💸 ليس لديك رصيد متاح لإضافة وظيفة جديدة", "error")

            user_identifier = current_user.email if current_user.is_authenticated else "visitor"
            send_slack_notification(f"A new job listing tried by {user_identifier} without credits")

            return render_template("jobs/add.html", form=form)

        # Calculate job expiration from the order's package duration
        duration_days = valid_order.package.duration_days
        job_expires_at = datetime.utcnow() + timedelta(days=duration_days)

        category_name = (Category.query.filter_by(id=form.category_id.data).first()).name
        city_name = (City.query.filter_by(id=form.city_id.data).first()).name
        generated_key = str(uuid.uuid4())

        # Create the job and attach it to the valid order
        job = Job(
            slug=f"{slugify(form.title.data)}-{category_name}-{city_name}-{generated_key}",
            title=form.title.data,
            description=form.description.data,
            category_id=form.category_id.data,
            city_id=form.city_id.data,
            user_id=current_user.id,
            order_id=valid_order.id,
            created_at=datetime.utcnow(),
            expires_at=job_expires_at
        )

        valid_order.posts_used += 1
        db.session.add(job)
        db.session.commit()

        # user = get_user_info(current_user.id)
        # if can_post_today():
        #     post_result = post_to_social_media(
        #         category_name,
        #         city_name,
        #         company_name=current_user.company_name if current_user.is_authenticated else "",
        #         job_title=form.title.data,
        #         logo_url= user['logo_url'] if user['logo_url'] else None
        #     )

        #     if post_result["status"]:
        #         social_post = SocialPost(job_id=job.id)
        #         db.session.add(social_post)
        #         db.session.commit()


        flash("🎉 تم إضافة الوظيفة بنجاح", "success")

        user_identifier = current_user.email if current_user.is_authenticated else "visitor"
        send_slack_notification(f"A new job listing by {user_identifier}")

        return redirect(request.referrer or '/') 

    return render_template("jobs/add.html", form=form, credits=credits)


@job_listing.route('/<job_id>')
def single_job(job_id):
    try:
        raw_job = Job.query.filter_by(slug = job_id).first_or_404()
        user = get_user_info(raw_job.user_id)
    except Exception as e:
        print(e)
        flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")
        return redirect('/')

    job = {
        "job": raw_job,
        "user": user
    }

    other_jobs = []

    return render_template('jobs/show.html', job=job, other_jobs=other_jobs, r2_public_url=os.getenv('R2_PUBLIC_URL'))


@job_listing.route('/s/<job_id>')
def single_scraped_job(job_id):
    try:
        raw_job = ScrapedJob.query.filter_by(slug = job_id).first_or_404()
    except Exception as e:
        print(e)
        flash("😔 حدث خطأ، يرجى المحاولة لاحقاً", "error")
        return redirect('/')

    job = raw_job

    other_jobs = []

    return render_template('jobs/show_scraped_job.html', job=job, other_jobs=other_jobs, r2_public_url=os.getenv('R2_PUBLIC_URL'))


@job_listing.route('/delete/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)

    if job.user_id != current_user.id:
        flash("🚫 لا يمكنك حذف وظيفة لا تملكها", "error")
        return redirect(url_for('job_listing.my_jobs'))

    db.session.delete(job)
    db.session.commit()

    user_identifier = current_user.email if current_user.is_authenticated else "visitor"
    send_slack_notification(f"A job listing deleted by {user_identifier}")

    flash("✅ تم حذف الوظيفة بنجاح", "success")
    return redirect(url_for('job_listing.my_jobs'))



@job_listing.route("/my-jobs")
@login_required
def my_jobs():
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category')
    city_id = request.args.get('city')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Start with jobs belonging to the current user
    query = Job.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if city_id:
        query = query.filter_by(city_id=city_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    raw_jobs = pagination.items

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
        'jobs/my-jobs.html',
        jobs=jobs,
        pagination=pagination,
        r2_public_url=os.getenv('R2_PUBLIC_URL'),
        cities=cities,
        categories=categories,
        current_search=search,
        current_category=category_id,
        current_city=city_id
    )