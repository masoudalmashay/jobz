from datetime import datetime, timedelta
import random
from sqlalchemy import func
from .models.social_post import SocialPost
from .extensions import db

import requests
import os

from dotenv import load_dotenv

load_dotenv()

def can_post_today():
    today = datetime.utcnow().date()

    last_post = db.session.query(SocialPost).order_by(SocialPost.posted_at.desc()).first()

    if last_post:
        last_post_day = last_post.posted_at.date()

        if last_post_day == today:
            return False

        delta_days = (today - last_post_day).days
        if delta_days < 2:
            return False

    return True

def post_on_facebook(content="", image_url=None):
    page_id = os.getenv('FACEBOOK_PAGE_ID')
    post_url = f'https://graph.facebook.com/{page_id}/photos'
    payload = {
        'url': image_url if image_url else '',
        'caption': content,
        'access_token': os.getenv('META_TOKEN')
    }
    response = requests.post(post_url, data=payload)
    print(response.text)

    if response.status_code == 200 or response.status_code == 201:
        return True

    return False

def post_on_instagram(content="", image_url=None):
    instagram_id = os.getenv('FACEBOOK_PAGE_ID')
    post_url = f'https://graph.facebook.com/{instagram_id}/media'
    payload = {
        'image_url': image_url if image_url else '',
        'caption': content,
        'access_token': os.getenv('META_TOKEN')
    }
    response = requests.post(post_url, data=payload)
    print(response.text)

    if response.status_code == 200 or response.status_code == 201:
        return True

    return False

def post_on_tiktok():
    pass

def giphy_trending():
    giphies = {
        'thursday': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOW1rZ3FmOWhlbndqYmU5dGt2NDE5c21wdGkzM2E4azhmOHRscmZ3YSZlcD12MV9naWZzX3RyZW5kaW5nJmN0PWc/X40g3tW0WUgIIidy6f/giphy.gif',
        'good_morning': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOW1rZ3FmOWhlbndqYmU5dGt2NDE5c21wdGkzM2E4azhmOHRscmZ3YSZlcD12MV9naWZzX3RyZW5kaW5nJmN0PWc/8cOkSOuvIChHNYOyP7/giphy.gif',
        'happy': 'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3bGduMDA0d2YxcHBwZjB6MXZsMmo4OW01NjR1NmV6ZWp5ZGplZW53dSZlcD12MV9naWZzX3RyZW5kaW5nJmN0PWc/6FxJBpNTBgWdJCXKD4/giphy.gif',
        'friday': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZnpnbHJnNXFnZW9ja3RmMmQ4bzN0OGlqYnNyenh0cmw2c2dwbDNzYSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/1x2Vv2luqAEJd0nbO1/giphy.gif',
        'do_not_give_up': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2UxaGFpemhldXg5NmttbzNiOGZlY3ZybHdqNXF0aXBsM21hZHNnYyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/2uh5yKKmZjDFUy2DOM/giphy.gif',
        'good_night': 'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnhwd2o0eWZ5N3F3MXhkbTN4bnV2cWplcnAwdjdueW44dzF0bGczciZlcD12MV9naWZzX3NlYXJjaCZjdD1n/wagHaQhJNaugXh3Zw6/giphy.gif'
    }

    now = datetime.now()
    weekday = now.weekday()  # Monday=0, Sunday=6
    hour = now.hour

    # Thursday
    if weekday == 3:
        return giphies['thursday']

    # Friday
    if weekday == 4:
        return giphies['friday']

    # Other days
    if 6 <= hour < 11:  # Morning 6AM-11AM
        return giphies['good_morning']
    elif hour >= 22 or hour < 6:  # Night 10PM-6AM
        return giphies['good_night']
    else:
        # Randomly select from 'happy' or 'do_not_give_up'
        return random.choice([giphies['happy'], giphies['do_not_give_up']])


def time_since(created_at):
    now = datetime.utcnow()
    diff = now - created_at

    days = diff.days
    seconds = diff.seconds

    if days > 0:
        return f"{days} ي" if days > 1 else "ي"
    elif seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} س" if hours > 1 else "س"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} د" if minutes > 1 else "د"
    else:
        return "الآن"
    


def mark_jobs(jobs):
    """
    Add marks/flags to jobs based on certain criteria.
    Example flags: 'is_hot', 'is_new'.
    """
    from datetime import datetime, timedelta
    from collections import defaultdict

    new_threshold_days = 3
    hot_threshold_days = 7
    hot_min_jobs = 3

    now = datetime.utcnow()

    # Track how many jobs each user posted in the last week
    recent_jobs_count = defaultdict(int)
    for entry in jobs:
        job = entry['job']
        posted_date = getattr(job, 'created_at', now)
        if (now - posted_date) <= timedelta(days=hot_threshold_days):
            recent_jobs_count[job.user_id] += 1

    marked = []
    for entry in jobs:
        job = entry['job']
        posted_date = getattr(job, 'created_at', now)

        is_new = (now - posted_date) <= timedelta(days=new_threshold_days)
        is_hot = (now - posted_date) <= timedelta(days=hot_threshold_days) and recent_jobs_count[job.user_id] >= hot_min_jobs

        entry.update({
            'is_new': is_new,
            'is_hot': is_hot
        })

        marked.append(entry)

    return marked

