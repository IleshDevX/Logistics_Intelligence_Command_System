"""
Quick verification script to check MongoDB collections
"""
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["lics_db"]

print("\n✅ Connected to MongoDB: lics_db")
print(f"📊 Collections: {db.list_collection_names()}")
print(f"📈 Total collections: {len(db.list_collection_names())}\n")

for collection_name in db.list_collection_names():
    print(f"   ✅ {collection_name}")

client.close()
