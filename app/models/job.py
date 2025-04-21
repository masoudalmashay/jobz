from app.extensions import db

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)


    def __init__(self, title, description):
        self.title = title
        self.description = description


    def __repr__(self):
        return f"<Job(title={self.title}, description={self.description})>"