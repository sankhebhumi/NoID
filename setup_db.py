import os
from pymongo import MongoClient
import pymongo.errors

def setup_database():
    print("Setting up MongoDB database...")
    
    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        # Test connection
        client.admin.command('ping')
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Error: Could not connect to MongoDB server on localhost:27017.")
        print("Please ensure MongoDB service or mongod is running locally, or set the MONGO_URI environment variable.")
        return

    db = client['noid_db']
    
    users_col = db['users']
    access_log_col = db['access_log']
    
    # Create unique index on pid
    users_col.create_index('pid', unique=True)
    access_log_col.create_index('pid', unique=True)
    
    sample_users = [
        {'pid': 'PID123', 'name': 'John Doe', 'department': 'Computer Science', 'year': '2024', 'program': 'B.Tech', 'dob': '2000-01-15'},
        {'pid': 'PID456', 'name': 'Jane Smith', 'department': 'Information Tech', 'year': '2025', 'program': 'B.Tech', 'dob': '2001-05-20'}
    ]
    
    for u in sample_users:
        users_col.update_one({'pid': u['pid']}, {'$set': u}, upsert=True)
        
    print("Database setup completed successfully! MongoDB 'noid_db' collections and sample data created.")

if __name__ == '__main__':
    setup_database()
