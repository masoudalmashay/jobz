import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
from supabase import create_client
from flask_login import LoginManager
import boto3

from botocore.config import Config

boto_config = Config(
    retries={'max_attempts': 5, 'mode': 'standard'},
    connect_timeout=30,
    read_timeout=60
)

load_dotenv()

subabase_url = os.getenv("SUPABASE_URL")
subabase_key = os.getenv("SUPABASE_KEY")


supabase = create_client(subabase_url, subabase_key) 
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