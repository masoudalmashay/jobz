import os
from flask import Flask
from dotenv import load_dotenv
from app.lib import time_since
from .routes.auth import auth
from .routes.main import main
from .routes.errors import errors
from .routes.profile import profile
from .routes.job_listing import job_listing
from .routes.payment import payment


from .extensions import db, migrate, login_manager, limiter
# from app.scheduler import start as start_scheduler

load_dotenv()

def create_app():
    
    app = Flask(__name__)

    app.secret_key = os.getenv('SECRET_KEY')

    limiter.init_app(app)

    NEON_PASSWORD = os.getenv('NEON_PASSWORD')
    NEON_DB = os.getenv('NEON_DB')

    NEON_USER = os.getenv('NEON_USER')

    
    # app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{NEON_USER}:{NEON_PASSWORD}@ep-old-credit-a2b3vbqj-pooler.eu-central-1.aws.neon.tech/{NEON_DB}?sslmode=require"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')
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
    from .models import social_post
    from .models import scraped_job
    

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

    # filters
    app.jinja_env.globals.update(time_since=time_since)



    # start_scheduler(app) # vercel does not support background tasks, so i comment this out
    return app