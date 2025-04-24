from app.extensions import db
from datetime import datetime
from flask import current_app


class Job(db.Model):
    __tablename__ = 'job'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)


    user_id = db.Column(db.String(255), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)


    def __repr__(self):
        return f"<Job(title={self.title}, description={self.description})>"
    

    # adding scheduled functions here

    # Function to delete expired jobs
    @staticmethod
    def delete_expired_jobs():
        """Delete expired jobs."""
        now = datetime.utcnow()
        expired_jobs = Job.query.filter(Job.expires_at < now).all()  # Get all expired jobs
        for job in expired_jobs:
            db.session.delete(job)  # Delete each expired job
        db.session.commit()  # Commit the changes