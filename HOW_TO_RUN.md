# How to Run main.py (FastAPI Backend) on Localhost

## 🚀 Quick Start

### Method 1: Direct Python Execution (Simplest)
```bash
python main.py
```
This will start the server on:
- **Host**: `0.0.0.0` (accessible from all interfaces)
- **Port**: `8000` (default, or set via `PORT` environment variable)
- **Auto-reload**: Enabled (restarts on code changes)

### Method 2: Using Uvicorn Directly
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Method 3: Using Uvicorn with Custom Settings
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
```

## 📍 Access URLs

Once running, access:
- **API Root**: http://localhost:8000
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## ⚙️ Configuration

### Environment Variables
Set these in your `.env` file or export them:

```bash
# Server Configuration
PORT=8000              # Server port (default: 8000)
HOST=0.0.0.0          # Host address (default: 0.0.0.0)

# Required Database & Services
MONGODB_URL=your_mongodb_connection_string
JWT_SECRET_KEY=your_secret_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_PHONE=+18159085835
```

### Change Port (PowerShell)
```powershell
$env:PORT=8080
python main.py
```

### Change Port (Bash/Linux/Mac)
```bash
export PORT=8080
python main.py
```

## 🐛 Troubleshooting

### Server Won't Start

1. **Check MongoDB Connection**
   - Ensure `MONGODB_URL` is set correctly in `.env`
   - Test MongoDB connection separately

2. **Check Required Environment Variables**
   - Run `python check_config.py` to verify all required variables are set

3. **Check Port Availability**
   ```bash
   # PowerShell
   netstat -ano | findstr ":8000"
   
   # If port is in use, change PORT or stop the process using it
   ```

4. **View Error Messages**
   - Run `python main.py` in foreground (not background) to see errors
   - Check terminal/console output for detailed error messages

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'uvicorn'`
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

**Issue**: `Missing required Twilio credentials`
**Solution**: Set all Twilio environment variables in `.env`

**Issue**: `MongoDB connection failed`
**Solution**: 
- Check `MONGODB_URL` in `.env`
- Verify MongoDB is running and accessible
- Test connection: `mongosh "your_connection_string"`

**Issue**: Port 8000 already in use
**Solution**: 
- Change port: `$env:PORT=8080; python main.py`
- Or stop the process using port 8000

## 📝 Step-by-Step Example

### Windows PowerShell:
```powershell
# 1. Navigate to project directory
cd "E:\Master Ki Kakshaa\07 Logistics Intelligence & Command System (LICS)"

# 2. Verify configuration
python check_config.py

# 3. Run the server
python main.py
```

### Linux/Mac/Bash:
```bash
# 1. Navigate to project directory
cd "/path/to/project"

# 2. Verify configuration
python check_config.py

# 3. Run the server
python main.py
```

## 🔍 Verify Server is Running

### Check if server is listening:
```bash
# PowerShell
netstat -ano | findstr ":8000"

# Linux/Mac
netstat -an | grep :8000
# or
lsof -i :8000
```

### Test API endpoint:
```bash
# PowerShell
curl http://localhost:8000/health

# Or in browser, visit:
http://localhost:8000/health
```

## 🎯 Expected Output

When running successfully, you should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Database connected successfully
INFO:     Authentication system initialized
INFO:     Notification manager initialized
INFO:     Twilio SMS service initialized successfully with FROM phone: +18159085835
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 🛑 Stop Server

Press `Ctrl+C` in the terminal where the server is running.

