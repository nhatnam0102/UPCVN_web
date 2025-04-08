from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime

# Setup MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client.get_database("upcvn")

# User data to import
users = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": generate_password_hash("admin123"),
        "is_admin": True,
        "created_at": datetime.utcnow(),
    },
    {
        "username": "user1",
        "email": "user1@example.com",
        "password_hash": generate_password_hash("user123"),
        "is_admin": False,
        "created_at": datetime.utcnow(),
    },
    {
        "username": "user2",
        "email": "user2@example.com",
        "password_hash": generate_password_hash("user123"),
        "is_admin": False,
        "created_at": datetime.utcnow(),
    },
]

# Insert users into the database
if db.users.count_documents({}) == 0:
    db.users.insert_many(users)
    print("Users imported successfully.")
else:
    print("Users already exist in the database.")
