import os
from flask import Flask
from dotenv import load_dotenv

from .routes.auth import auth
from .routes.main import main
from .routes.errors import errors
from .routes.profile import profile
from .routes.job_listing import job_listing
from .routes.payment import payment


from .extensions import db, migrate, login_manager
from app.scheduler import start as start_scheduler

load_dotenv()

def create_app():
    
    app = Flask(__name__)

    NEON_PASSWORD = os.getenv('NEON_PASSWORD')
    NEON_DB = os.getenv('NEON_DB')

    NEON_USER = os.getenv('NEON_USER')

    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{NEON_USER}:{NEON_PASSWORD}@ep-old-credit-a2b3vbqj-pooler.eu-central-1.aws.neon.tech/{NEON_DB}?sslmode=require"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'your_super_secret_key_here'
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    import datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now()}
    

    db.init_app(app)

    from .models import category
    from .models import city
    from .models import package
    from .models import order
    from .models import job
    

    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "🔑 قم بتسجيل الدخول للوصول إلى هذه الصفحة"
    login_manager.login_message_category = "warning"



    # register blueprints here
    app.register_blueprint(auth)
    app.register_blueprint(main, url_prefix="/")
    app.register_blueprint(errors)
    app.register_blueprint(profile, url_prefix="/account")
    app.register_blueprint(job_listing, url_prefix="/jobs")
    app.register_blueprint(payment, url_prefix="/payments")


    start_scheduler(app)
    return app