from app.extensions import db
from datetime import datetime

class SocialPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
