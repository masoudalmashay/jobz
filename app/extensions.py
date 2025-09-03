import os
import requests
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
from supabase import create_client, ClientOptions
from flask_login import LoginManager
import boto3
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from botocore.config import Config




    
import json
import urllib.request

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

limiter = Limiter(
    get_remote_address,
    default_limits=["1000 per day", "200 per hour"]
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


def send_slack_notification(message):
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL environment variable is missing")

    data = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(slack_webhook_url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            print("✅ Slack notification sent successfully!")
            return response.status
    except Exception as e:
        print(f"Failed to send message to Slack: {e}")
        return None


def generate_image_template(job_cat, job_place, company_name, job_title, logo_url=None):

    url = f"{os.getenv('APITEMPLATE_URL')}/create-image?template_id={os.getenv('APITEMPLATE_ID')}"
    token = os.getenv('APITEMPLATE_TOKEN')

    payload = {
                "overrides": [
                    {
                        "name": "job_title",
                        "text": job_title
                    },
                    {
                        "name": "job_cat",
                        "text": job_cat
                    },
                    {
                        "name": "job_place",
                        "text": job_place
                    },
                    {
                        "name": "job_company",
                        "text": company_name
                    },
                    {
                        "name": "logo" if logo_url else "no_logo",
                        "src": logo_url
                    }
                ]
            }

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": token,
        "authorization": f"Bearer {token}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return {"status": True, "data": response.json()}
    else:
        return {"status": False, "error": response.json()}
    

def post_to_social_media(job_cat, job_place, company_name, job_title, logo_url=None):
    result = generate_image_template(job_cat, job_place, company_name, job_title, logo_url)
    profile_ids = ['facebook', 'twitter', 'tiktok']
    post_content = f"""
    فرصة عمل جديدة في مجال {job_cat} \n
    بمدينة {job_place} \n
    في شركة {company_name} \n
    الوظيفة {job_title}.
    \n\n\n
    #وظائف_ليبيا #gowork #{job_cat.replace(' ', '_')}
    """
    if result['status'] and result['data']['status'] == "success":
        url = f"{os.getenv('AYSHARE_URL')}/post"
        token = os.getenv('AYSHARE_TOKEN')

        payload = {
            "post": post_content,
            "platforms": profile_ids,
            "mediaUrls": [result['data']['download_url_png']]
        }

        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {token}"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return {"status": True, "data": response.json()}
        else:
            return {"status": False, "error": response.json()}
        


    return {"status": False, "error": "something went wrong"}


