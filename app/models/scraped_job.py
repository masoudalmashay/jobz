from app.extensions import db
from datetime import datetime
from flask import current_app


class ScrapedJob(db.Model):
    __tablename__ = 'scraped_job'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)


    company_name = db.Column(db.String(255), nullable=False)
    logo_url = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)


