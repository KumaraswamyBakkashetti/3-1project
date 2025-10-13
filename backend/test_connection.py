"""
Test MongoDB Connection
Run this to verify your MongoDB Atlas connection
"""
from database import Database

try:
    print("Connecting to MongoDB...")
    db = Database()
    print("✓ Connected successfully!")
    print(f"Database: {db.db.name}")
    print(f"Collections: {db.db.list_collection_names()}")
    print(f"Users count: {db.users.count_documents({})}")
    print("\n✓ MongoDB Atlas is working correctly!")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check your MONGODB_URI in .env file")
    print("2. Verify username/password in connection string")
    print("3. Check Network Access in Atlas (allow your IP)")
    print("4. Make sure cluster is running in Atlas dashboard")
