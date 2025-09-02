from app import create_app 
from flask_limiter.errors import RateLimitExceeded
from flask import flash, redirect, request, url_for
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()


@app.errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    endpoint = request.endpoint
    if endpoint == "auth.login":
        msg = "🔒 لقد تجاوزت الحد الأقصى لمحاولات تسجيل الدخول. حاول لاحقاً."
    elif endpoint == "auth.register":
        msg = "📧 حاولت إنشاء حسابات كثيرة بسرعة. حاول لاحقاً."
    else:
        msg = "🚫 لقد وصلت للحد الأقصى من الطلبات. حاول لاحقاً."

    flash(msg, "error")
    return redirect(url_for("main.home"))

if __name__ == "__main__":
        app.run(debug= True if os.getenv('FLASK_ENV') == 'development' else False) # Set debug=True for development purposes