from app.extensions import db



class Package(db.Model):
    __tablename__ = 'package'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    post_count = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)  # e.g., 30 for 30-day posting
    orders = db.relationship('Order', backref='package', lazy=True)
