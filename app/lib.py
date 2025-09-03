from datetime import datetime, timedelta
from sqlalchemy import func
from .models.social_post import SocialPost

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