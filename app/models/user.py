from flask_login import UserMixin
from app.extensions import db

class User(UserMixin):
    def __init__(self, id, email, email_verified, company_name, phone, logo_url):
        self.id = id
        self.email = email
        self.email_verified = email_verified
        self.company_name = company_name
        self.phone = phone
        self.logo_url = logo_url

    def get_id(self):
        return self.id