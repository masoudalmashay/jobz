from flask import Flask

from supabase import create_client

subabase_url = "https://lbxtfvcfpnyitmksatzh.supabase.co"
subabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxieHRmdmNmcG55aXRta3NhdHpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ5ODA0ODcsImV4cCI6MjA2MDU1NjQ4N30.hvf7jLfQkGl5axbZ3-yEpq0Rfg9AA6f6P_DWC5_0R7s"

client = create_client(subabase_url, subabase_key)

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello from Flask!"

@app.route("/register")
def register():
    email = "inky.9drp@gmail.com"
    password = "123456789"

    # Create a new user
    try:
        response = client.auth.sign_up({"email": email, "password": password, "options": {"data": {"name": "Masoud"}}})
    except Exception as e:
        return f"Error creating user: {str(e)}"

    user = response.user

    if user:
        return f"User created successfully! {user.user_metadata['name']}"
    else:
        return "Unknown error occurred."


@app.route("/login")
def login():

    return "Login page"





