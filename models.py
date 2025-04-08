from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime


def db_setup(db):
    class User(UserMixin):
        def __init__(self, user_data):
            self.id = str(user_data["_id"])
            self.username = user_data["username"]
            self.email = user_data["email"]
            self.password_hash = user_data["password_hash"]
            self.is_admin = user_data.get("is_admin", False)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        @staticmethod
        def generate_password_hash(password):
            return generate_password_hash(password)

        @staticmethod
        def get_by_id(user_id):
            user_data = db.users.find_one({"_id": ObjectId(user_id)})
            return User(user_data) if user_data else None

        @staticmethod
        def get_by_username(username):
            user_data = db.users.find_one({"username": username})
            return User(user_data) if user_data else None

    # Define other models as needed (e.g., Product, CaseStudy, etc.)
    # These will be simple dictionaries stored in MongoDB, so no need for SQLAlchemy models.

    return (
        User,
        None,
        None,
        None,
        None,
        None,
        None,
    )  # Replace `None` with actual models if needed
