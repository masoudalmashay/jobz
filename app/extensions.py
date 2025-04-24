import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
from supabase import create_client, ClientOptions
from flask_login import LoginManager
import boto3


from botocore.config import Config

boto_config = Config(
    retries={'max_attempts': 5, 'mode': 'standard'},
    connect_timeout=30,
    read_timeout=60
)

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_service_role = os.getenv("SUPABASE_SERVICE_ROLE")


supabase = create_client(supabase_url, supabase_key) 
supabase_admin = create_client(
    supabase_url,
    supabase_service_role,
    options=ClientOptions(
        auto_refresh_token=False,
        persist_session=False,
    )
)



db = SQLAlchemy()


migrate = Migrate()
login_manager = LoginManager()

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("R2_ENDPOINT"),
    aws_access_key_id=os.getenv("R2_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("R2_SECRET_KEY"),
    config=boto_config
)


def get_user_info(user_id):
    response = supabase_admin.auth.admin.get_user_by_id(user_id)
    try:
        return {
        'id': response.user.id,
        'email': response.user.email,
        'email_varified': response.user.user_metadata['email_confirmed'],
        'company_name': response.user.user_metadata['company_name'],
        'phone': response.user.user_metadata['phone'],
        'logo_url': response.user.user_metadata['logo_url']
    }
    except Exception as e:
        return None


