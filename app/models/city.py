from app.extensions import db

class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    jobs = db.relationship('Job', backref='city', lazy=True)
