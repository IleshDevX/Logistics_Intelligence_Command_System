# 🗃️ MongoDB Connection Guide for LICS

**Status:** ✅ MongoDB is already connected and working!  
**Database:** `lics_db`  
**Collections:** 6 ready  

---

## ✅ Current Connection Status

Your MongoDB is **already configured and connected**:
- ✅ MongoDB Service: Running on `localhost:27017`
- ✅ Database: `lics_db` created
- ✅ Collections: 6 collections with schemas and indexes
- ✅ Python Connection: Working via `database/connection.py`

**You don't need to do anything for local development!**

---

## 📊 View Your Database

### Option 1: MongoDB Compass (Recommended - GUI)

1. **Open MongoDB Compass** (already installed on your system)
2. **Connection String:**
   ```
   mongodb://localhost:27017/
   ```
3. **Click "Connect"**
4. **Navigate to:** `lics_db` database
5. **You'll see all 6 collections:**
   - users
   - shipments
   - risk_scores
   - decisions
   - notifications
   - learning_logs

6. **Click any collection** to see documents (currently empty)

### Option 2: MongoDB Shell (mongosh)

```powershell
# Open MongoDB shell
mongosh

# Switch to your database
use lics_db

# List all collections
show collections

# View users collection
db.users.find()

# Count documents
db.users.countDocuments()

# View with pretty formatting
db.users.find().pretty()
```

### Option 3: Python Script (Quick Check)

Run this to see your database status:
```powershell
& ".\backend\venv\Scripts\python.exe" ".\database\verify_collections.py"
```

---

## 🚀 For Streamlit Deployment

### Important: Connection Configuration

Your current setup uses **localhost** which works for local development, but for Streamlit Cloud deployment, you'll need to update the connection.

### Step 1: Update Connection for Cloud Deployment

The connection is already configured to use environment variables in `database/connection.py`:

```python
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "lics_db")
```

This means:
- ✅ **Local:** Uses `localhost:27017` (default)
- ✅ **Cloud:** Uses environment variable from Streamlit secrets

### Step 2: For Streamlit Cloud - Use MongoDB Atlas

Since Streamlit Cloud can't access your local MongoDB, you'll need **MongoDB Atlas** (free cloud database):

#### A. Create MongoDB Atlas Account (FREE)

1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Sign up for free account
3. Create a **FREE M0 Cluster** (512MB storage, perfect for LICS)
4. Choose a region close to you (AWS/GCP/Azure)

#### B. Create Database User

1. In Atlas, go to **Database Access**
2. Click **"Add New Database User"**
3. Create user:
   - Username: `lics_user`
   - Password: `<generate strong password>`
   - Role: **Atlas Admin** or **Read and write to any database**
4. **Save password securely!**

#### C. Whitelist IP Addresses

1. Go to **Network Access**
2. Click **"Add IP Address"**
3. Choose **"Allow Access from Anywhere"** (0.0.0.0/0)
   - For production, use specific IPs only
4. Click **Confirm**

#### D. Get Connection String

1. Go to **Database** → **Connect**
2. Choose **"Connect your application"**
3. Copy the connection string:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Replace `<username>` and `<password>` with your credentials

Example:
```
mongodb+srv://lics_user:MySecurePass123@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
```

#### E. Migrate Collections to Atlas

Run this script to create collections in Atlas:

```powershell
# Set environment variable to Atlas URI
$env:MONGO_URI="mongodb+srv://lics_user:password@cluster0.xxxxx.mongodb.net/"
$env:DATABASE_NAME="lics_db"

# Run setup script
& ".\backend\venv\Scripts\python.exe" ".\database\setup_mongodb.py"
```

---

## 🔧 Streamlit Configuration

### Step 1: Create `.streamlit/secrets.toml`

Create this file in your project root:

```toml
# .streamlit/secrets.toml

# MongoDB Configuration
[mongodb]
uri = "mongodb+srv://lics_user:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
database = "lics_db"

# JWT Configuration
[jwt]
secret_key = "your-super-secret-jwt-key-here"
algorithm = "HS256"
access_token_expire_minutes = 1440
```

**⚠️ IMPORTANT:** Add this to `.gitignore`:
```
.streamlit/secrets.toml
.env
```

### Step 2: Update Connection Code for Streamlit

Modify `database/connection.py` to support Streamlit secrets:

```python
import os

# Check if running in Streamlit
try:
    import streamlit as st
    # Use Streamlit secrets if available
    MONGO_URI = st.secrets.get("mongodb", {}).get("uri", os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    DATABASE_NAME = st.secrets.get("mongodb", {}).get("database", os.getenv("DATABASE_NAME", "lics_db"))
except ImportError:
    # Running in FastAPI/backend - use env variables
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "lics_db")
```

### Step 3: Deploy to Streamlit Cloud

1. **Push code to GitHub**
   ```powershell
   git add .
   git commit -m "Add MongoDB Atlas support"
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"

3. **Configure App**
   - Repository: `IleshDevX/07-Logistics-Intelligence---Command-System--LICS-`
   - Branch: `main`
   - Main file path: `dashboard/control_tower.py` (or your main Streamlit file)

4. **Add Secrets**
   - Click "Advanced settings"
   - Paste your `.streamlit/secrets.toml` content
   - Click "Save"

5. **Deploy!**
   - Streamlit will install dependencies and start your app
   - Your app will connect to MongoDB Atlas

---

## 📝 Current vs Cloud Setup

### Local Development (Current - Working ✅)
```
Your Computer
├── FastAPI Backend (localhost:8000)
├── MongoDB (localhost:27017)
└── Streamlit Dashboard (localhost:8501)
```

### Cloud Deployment (Streamlit Cloud)
```
Streamlit Cloud
├── Streamlit Dashboard (deployed)
├── FastAPI Backend (optional - can deploy to Heroku/Railway)
└── MongoDB Atlas (cloud database)
```

---

## 🎯 For Your Project

### Current Status:
✅ MongoDB running locally  
✅ 6 collections created  
✅ Connection working  
✅ Ready for local development  

### For Streamlit Cloud Deployment:
1. ⏳ Create MongoDB Atlas account (FREE)
2. ⏳ Migrate collections to Atlas
3. ⏳ Add connection string to Streamlit secrets
4. ⏳ Deploy to Streamlit Cloud

---

## 🔍 Quick Commands Reference

### Check MongoDB Status:
```powershell
Get-Service -Name MongoDB
```

### View Collections:
```powershell
& ".\backend\venv\Scripts\python.exe" ".\database\verify_collections.py"
```

### Start FastAPI with MongoDB:
```powershell
cd backend
& ".\venv\Scripts\uvicorn.exe" main:app --reload --port 8000
```

### Access MongoDB Compass:
- Open app → Connect to `mongodb://localhost:27017/`

---

## ❓ Common Questions

### Q: Can I see my data in MongoDB Compass?
**A:** Yes! Open Compass → Connect to `mongodb://localhost:27017/` → Open `lics_db` database

### Q: Is MongoDB installed correctly?
**A:** Yes! Your service is running and collections are created ✅

### Q: Will my local MongoDB work on Streamlit Cloud?
**A:** No, you need MongoDB Atlas (cloud) for Streamlit Cloud deployment

### Q: How do I keep data synced between local and cloud?
**A:** 
- Use local MongoDB for development
- Use MongoDB Atlas for production/Streamlit Cloud
- Export/import data when needed using `mongodump` and `mongorestore`

### Q: Is MongoDB Atlas free?
**A:** Yes! M0 cluster is FREE forever (512MB storage, 500 connections/day)

---

## 🚨 Important Notes

### Security:
- ✅ Never commit MongoDB credentials to GitHub
- ✅ Use `.gitignore` for `.env` and `secrets.toml`
- ✅ Use strong passwords
- ✅ Whitelist specific IPs in production (not 0.0.0.0/0)

### Cost:
- ✅ Local MongoDB: FREE
- ✅ MongoDB Atlas M0: FREE forever
- ✅ Streamlit Cloud: FREE for public apps

### Performance:
- ✅ Local development: Fast (localhost)
- ✅ Streamlit Cloud + Atlas: Depends on region proximity
- ✅ Connection pooling already configured (10-50 connections)

---

## ✅ Summary

**You're all set for local development!**

MongoDB is:
- ✅ Installed and running
- ✅ Connected to your backend
- ✅ 6 collections ready
- ✅ Working perfectly

**For Streamlit Cloud deployment:**
1. Create MongoDB Atlas account (15 minutes)
2. Migrate collections (5 minutes)
3. Add secrets to Streamlit (2 minutes)
4. Deploy! 🚀

---

**Need help with MongoDB Atlas setup? Just ask!**
