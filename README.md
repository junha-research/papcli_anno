# Annotation Tool

Expert evaluation tool for synthetic AES (Automated Essay Scoring) data with per-trait annotation system.

## 🚀 Quick Start (Windows)

### Prerequisites
- Python 3.9 or higher ([Download](https://www.python.org/downloads/))
- Node.js 18 or higher ([Download](https://nodejs.org/))
- Git ([Download](https://git-scm.com/downloads))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/junha-research/papcli_anno.git
   cd papcli_anno
   ```

2. **Run setup** (first time only)
   ```bash
   setup.bat
   ```
   This will:
   - Create Python virtual environment
   - Install all dependencies
   - Initialize the database with 5 mock essays and 4 test accounts
   - Build the frontend

3. **Start the application**
   ```bash
   start.bat
   ```
   This will open two windows:
   - Backend server (http://localhost:8000)
   - Frontend server (http://localhost:4173)

4. **Access the application**
   - Open your browser and go to: http://localhost:4173
   - Login with test accounts:
     - `annotator1` / `password123`
     - `annotator2` / `password123`
     - `annotator3` / `password123`
     - `annotator4` / `password123`

## 🌐 External Access Setup

To allow access from outside your local network:

1. **Configure external access**
   ```bash
   configure_external_access.bat
   ```
   Enter your public IP when prompted.

2. **Set up port forwarding** on your router:
   - Port 8000 → Backend
   - Port 4173 → Frontend

3. **Open Windows Firewall** (Run PowerShell as Administrator):
   ```powershell
   netsh advfirewall firewall add rule name="Annotation Backend" dir=in action=allow protocol=TCP localport=8000
   netsh advfirewall firewall add rule name="Annotation Frontend" dir=in action=allow protocol=TCP localport=4173
   ```

4. **Rebuild frontend**
   ```bash
   cd frontend
   npm run build
   ```

5. **Restart the application**
   ```bash
   start.bat
   ```

Users can now access at: `http://YOUR_PUBLIC_IP:4173`

## 📁 Project Structure

```
annotation-tool/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── auth.py          # Authentication
│   ├── init_db.py       # Database initialization
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/
│   │   ├── pages/      # Login, Dashboard, Annotate
│   │   ├── api/        # API client
│   │   └── store/      # State management
│   └── package.json    # Node dependencies
├── setup.bat           # Initial setup script
├── start.bat           # Start application
└── configure_external_access.bat  # External access setup
```

## 🎯 Features

- **User Authentication**: JWT-based authentication with 4 test accounts
- **Per-Trait Evaluation**: Independent scoring for Language, Organization, and Content
- **Sentence Selection**: Formula-based sentence selection (n_sc = round(n_se * (5 - score) / 5))
- **Progress Tracking**: Real-time annotation progress on dashboard
- **Data Persistence**: SQLite database for all annotations

## 📊 Data Export

Annotation data is stored in `backend/annotation.db`. To export:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('backend/annotation.db')
annotations = pd.read_sql_query("SELECT * FROM annotations", conn)
annotations.to_csv('annotations_export.csv', index=False)
conn.close()
```

## 🔧 Manual Commands

If you prefer manual control:

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run build
npm run preview -- --host 0.0.0.0 --port 4173
```

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚠️ Troubleshooting

### Port already in use
If ports 8000 or 4173 are already in use:
```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database issues
To reset the database:
```bash
cd backend
del annotation.db
python init_db.py
```

### Frontend not connecting to backend
1. Check `frontend/.env` file
2. Ensure backend is running
3. Check CORS settings in `backend/main.py`

## 📄 License

MIT License

## 👥 Contributors

- Junha (junha-research)
