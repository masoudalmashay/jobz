from app.extensions import db

from datetime import datetime

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)

    post_limit = db.Column(db.Integer, nullable=False)
    posts_used = db.Column(db.Integer, default=0)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    jobs = db.relationship('Job', backref='bundle', lazy=True)
