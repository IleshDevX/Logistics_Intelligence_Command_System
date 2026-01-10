# STREAMLIT DEPLOYMENT GUIDE
# =========================

## 🎯 Overview

Your LICS application is now **Streamlit Cloud Ready**! This guide explains:
- ✅ What we've configured for Streamlit compatibility
- 🚀 How to deploy to Streamlit Cloud
- 🔐 How to configure MongoDB Atlas
- 🛠️ Local development vs Cloud deployment

---

## ✅ What We've Done

### 1. **Database Connection (Streamlit Compatible)**
**File:** `database/connection.py`

Updated to support **dual-mode configuration**:
```python
# Automatically detects environment:
# 1. Streamlit Cloud → Uses st.secrets["mongodb"]
# 2. Local/FastAPI → Uses environment variables
```

**How it works:**
- Tries to import `streamlit` module
- If found, reads from `st.secrets["mongodb"]["uri"]`
- If not found, falls back to `os.getenv("MONGO_URI")`
- Seamless switching between local and cloud

### 2. **JWT Authentication (Streamlit Compatible)**
**File:** `backend/auth.py`

JWT configuration now supports:
```python
# Reads from st.secrets["jwt"] if available
# Falls back to environment variables
```

**Benefits:**
- Same code works in Streamlit and FastAPI
- No code changes needed for deployment
- Secure secret management via Streamlit Cloud

### 3. **Secrets Template Created**
**File:** `.streamlit/secrets.toml`

Template for all sensitive credentials:
- MongoDB Atlas connection string
- JWT secret key
- API backend URL
- App configuration

**SECURITY:** Added to `.gitignore` - NEVER commit this file!

---

## 🚀 Deployment Steps

### **STEP 1: Setup MongoDB Atlas (Cloud Database)**

#### Why MongoDB Atlas?
Streamlit Cloud cannot connect to `localhost:27017`. You need a cloud database.

#### Create MongoDB Atlas Account:
1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Sign up (free tier available)
3. Create a new project: "LICS"

#### Create Database Cluster:
1. Click **"Build a Database"**
2. Choose **M0 (Free)** tier
3. Select **Cloud Provider & Region** (choose closest to users)
4. Cluster Name: `lics-cluster`
5. Click **"Create Cluster"** (takes 3-5 minutes)

#### Create Database User:
1. Go to **Database Access** (left sidebar)
2. Click **"Add New Database User"**
3. Choose **Password** authentication
4. Username: `lics_admin`
5. Password: `<generate strong password>`
6. User Privileges: **"Read and write to any database"**
7. Click **"Add User"**

#### Configure Network Access:
1. Go to **Network Access** (left sidebar)
2. Click **"Add IP Address"**
3. Choose **"Allow Access from Anywhere"** (for Streamlit Cloud)
4. IP: `0.0.0.0/0` (auto-filled)
5. Click **"Confirm"**

**⚠️ Security Note:** For production, restrict to Streamlit Cloud IPs only.

#### Get Connection String:
1. Go to **Database** → **Clusters**
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Driver: **Python**, Version: **3.12 or later**
5. Copy connection string:
   ```
   mongodb+srv://lics_admin:<password>@lics-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with your actual password
7. **Save this string** - you'll need it for Streamlit secrets

---

### **STEP 2: Migrate Data to MongoDB Atlas**

#### Option A: Fresh Start (Recommended)
Just use the new Atlas database. Your setup script will create collections automatically.

#### Option B: Migrate Existing Data
If you have local data to migrate:

1. **Export from Local MongoDB:**
   ```powershell
   mongodump --uri="mongodb://localhost:27017/" --db=lics_db --out=./backup
   ```

2. **Import to MongoDB Atlas:**
   ```powershell
   mongorestore --uri="mongodb+srv://lics_admin:<password>@lics-cluster.xxxxx.mongodb.net/" --db=lics_db ./backup/lics_db
   ```

3. **Verify in MongoDB Compass:**
   - Connect to Atlas using connection string
   - Check that all 6 collections exist:
     - users
     - shipments
     - risk_scores
     - decisions
     - notifications
     - learning_logs

---

### **STEP 3: Configure Streamlit Secrets**

#### For Local Development:

1. **Update `.streamlit/secrets.toml`:**
   ```toml
   [mongodb]
   uri = "mongodb+srv://lics_admin:YOUR_PASSWORD@lics-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority"
   database = "lics_db"

   [jwt]
   secret_key = "your-super-secret-jwt-key-min-32-characters"
   algorithm = "HS256"
   access_token_expire_minutes = 1440

   [api]
   backend_url = "http://localhost:8000"

   [app]
   title = "LICS - Logistics Intelligence & Command System"
   debug_mode = true
   log_level = "DEBUG"
   ```

2. **Test Locally:**
   ```powershell
   cd "E:\Master Ki Kakshaa\07 Logistics Intelligence & Command System (LICS)"
   streamlit run dashboard/control_tower.py
   ```

#### For Streamlit Cloud Deployment:

1. **Push Code to GitHub:**
   ```powershell
   git add .
   git commit -m "Add Streamlit Cloud compatibility"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to: https://share.streamlit.io/
   - Sign in with GitHub
   - Click **"New app"**
   - Repository: Select your repo
   - Branch: `main`
   - Main file path: `dashboard/control_tower.py`
   - Click **"Deploy!"**

3. **Configure Secrets in Streamlit Cloud:**
   - Go to your deployed app
   - Click **⋮** (three dots) → **Settings**
   - Click **"Secrets"** in left sidebar
   - Paste your secrets (same format as `.streamlit/secrets.toml`):
   ```toml
   [mongodb]
   uri = "mongodb+srv://lics_admin:YOUR_PASSWORD@lics-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority"
   database = "lics_db"

   [jwt]
   secret_key = "your-super-secret-jwt-key-min-32-characters"
   algorithm = "HS256"
   access_token_expire_minutes = 1440

   [api]
   backend_url = "https://your-fastapi-backend.herokuapp.com"  # If separate

   [app]
   title = "LICS - Logistics Intelligence & Command System"
   debug_mode = false
   log_level = "INFO"
   ```
   - Click **"Save"**
   - App will automatically restart with new secrets

---

## 🛠️ Architecture Options

### **Option 1: Streamlit + Embedded FastAPI (Recommended for Start)**

**Structure:**
```
Streamlit App (Frontend)
    └── Embedded FastAPI (Backend via subprocess)
        └── MongoDB Atlas (Database)
```

**Pros:**
- Single deployment
- Easier to manage
- Free tier friendly

**Cons:**
- FastAPI restarts when Streamlit restarts
- Limited scalability

**Implementation:**
Create `dashboard/control_tower.py`:
```python
import streamlit as st
import subprocess
import time
import requests

# Start FastAPI backend on first run
if 'backend_started' not in st.session_state:
    subprocess.Popen([
        "python", "-m", "uvicorn",
        "api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])
    time.sleep(3)  # Wait for startup
    st.session_state.backend_started = True

# Now use FastAPI endpoints
response = requests.get("http://localhost:8000/")
st.json(response.json())
```

---

### **Option 2: Streamlit + Separate FastAPI (Production Ready)**

**Structure:**
```
Streamlit Cloud (Frontend)
    └── API Calls via HTTP
        └── Heroku/Railway/Render (FastAPI Backend)
            └── MongoDB Atlas (Database)
```

**Pros:**
- Independent scaling
- Better performance
- Production-grade

**Cons:**
- Two separate deployments
- More complex setup

**FastAPI Deployment Options:**
1. **Heroku:** https://www.heroku.com/ (Free tier available)
2. **Railway:** https://railway.app/ (Free $5/month credit)
3. **Render:** https://render.com/ (Free tier available)

**Update Streamlit secrets:**
```toml
[api]
backend_url = "https://lics-backend.herokuapp.com"  # Your deployed FastAPI URL
```

---

## 🧪 Testing Configuration

### Test MongoDB Connection:
```python
# Run in Python or Streamlit
import streamlit as st
from database.connection import db_connection

if db_connection.connect():
    st.success(f"✅ Connected to MongoDB: {db_connection.DATABASE_NAME}")
    collections = db_connection.db.list_collection_names()
    st.write(f"📊 Collections: {collections}")
else:
    st.error("❌ Failed to connect to MongoDB")
```

### Test JWT Configuration:
```python
# Run in Python or Streamlit
import streamlit as st
from backend.auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

st.write(f"🔐 JWT Algorithm: {ALGORITHM}")
st.write(f"⏱️ Token Expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
st.write(f"🔑 Secret Key: {'*' * 20} (hidden)")
```

---

## 📦 Required Files for Deployment

### **1. requirements.txt**
Must include all dependencies:
```txt
streamlit
fastapi
uvicorn
pymongo
python-jose[cryptography]
passlib[bcrypt]
python-multipart
email-validator
pydantic
requests
pandas
plotly
```

### **2. packages.txt** (for system dependencies)
Create if you need system packages:
```txt
# Add system packages here if needed
```

### **3. .streamlit/config.toml** (optional)
For Streamlit UI customization:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
```

---

## 🔐 Security Best Practices

### 1. **Never Commit Secrets**
```gitignore
# Already added to .gitignore:
.env
.streamlit/secrets.toml
```

### 2. **Use Strong JWT Secret**
```python
# Generate a secure secret:
import secrets
print(secrets.token_urlsafe(32))
# Output: Use this in st.secrets["jwt"]["secret_key"]
```

### 3. **Restrict MongoDB Network Access**
For production, replace `0.0.0.0/0` with specific IPs:
- Get Streamlit Cloud IPs (contact support or use VPC)
- Add only those IPs to MongoDB Atlas Network Access

### 4. **Use Environment-Specific Settings**
```toml
# Local (.streamlit/secrets.toml)
[app]
debug_mode = true
log_level = "DEBUG"

# Production (Streamlit Cloud Secrets)
[app]
debug_mode = false
log_level = "INFO"
```

---

## 🐛 Troubleshooting

### **Issue: "streamlit module not found"**
**Solution:** This is expected in FastAPI backend. The code automatically falls back to environment variables.

### **Issue: "Connection timeout to MongoDB"**
**Solution:** 
1. Check MongoDB Atlas Network Access allows `0.0.0.0/0`
2. Verify connection string has correct password
3. Test connection using MongoDB Compass first

### **Issue: "JWT token invalid"**
**Solution:**
1. Ensure same SECRET_KEY in both local and cloud
2. Check token hasn't expired (24 hours default)
3. Verify `st.secrets["jwt"]["secret_key"]` is set

### **Issue: "App keeps restarting"**
**Solution:**
1. Check Streamlit Cloud logs for errors
2. Verify all dependencies in `requirements.txt`
3. Ensure secrets are properly configured

---

## 📊 Current Status

✅ **Database Connection:** Streamlit Cloud compatible  
✅ **JWT Authentication:** Streamlit Cloud compatible  
✅ **Secrets Management:** Template created  
✅ **.gitignore:** Updated to exclude secrets  
⏳ **MongoDB Atlas:** Need to create account and cluster  
⏳ **Streamlit Dashboard:** Need to create/update UI  
⏳ **Cloud Deployment:** Ready when above steps complete  

---

## 🎓 Next Steps

1. **Immediate:**
   - [ ] Create MongoDB Atlas account
   - [ ] Setup cluster and get connection string
   - [ ] Update `.streamlit/secrets.toml` with Atlas URI
   - [ ] Test local Streamlit app with Atlas

2. **Short-term:**
   - [ ] Build Streamlit dashboard UI
   - [ ] Integrate FastAPI endpoints
   - [ ] Test authentication flow in Streamlit
   - [ ] Create user registration/login pages

3. **Deployment:**
   - [ ] Push code to GitHub
   - [ ] Deploy to Streamlit Cloud
   - [ ] Configure secrets in Streamlit Cloud
   - [ ] Test production deployment

---

## 📚 Resources

- **MongoDB Atlas:** https://www.mongodb.com/cloud/atlas
- **Streamlit Cloud:** https://share.streamlit.io/
- **Streamlit Docs:** https://docs.streamlit.io/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Streamlit Secrets:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

---

## 💡 Tips

1. **Test Locally First:** Always test with MongoDB Atlas locally before deploying to Streamlit Cloud
2. **Use MongoDB Compass:** Visual tool to verify Atlas connection and data
3. **Monitor Logs:** Streamlit Cloud provides real-time logs - use them for debugging
4. **Version Control:** Commit working code frequently
5. **Secrets Backup:** Save secrets in a secure password manager (not in code!)

---

**Ready to Deploy?** Follow the steps above, and your LICS will be live on Streamlit Cloud! 🚀
