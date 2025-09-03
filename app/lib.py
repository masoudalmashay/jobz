from datetime import datetime, timedelta
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