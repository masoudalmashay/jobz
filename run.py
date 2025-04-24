from app import create_app  # Assuming your __init__.py is in the same directory
# Load environment variables from the .env file

app = create_app()


if __name__ == "__main__":
        app.run(debug=True)

        start_scheduler()