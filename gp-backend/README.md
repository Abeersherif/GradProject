# 🏥 MedTwin Backend

Flask backend for MedTwin AI Medical Assistant

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
copy .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY
```

### 3. Run Server
```bash
python app.py
```

Server will start on: http://localhost:5000

## 📁 Project Structure

```
gp-backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── agents/               # AI Agents
│   └── medtwin_agents.py
├── routes/               # API endpoints
│   ├── auth.py          # Authentication routes
│   └── consultation.py  # Consultation routes
├── models/              # Database models
│   ├── user.py
│   ├── consultation.py
│   └── ticket.py
└── utils/               # Helper functions
```

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```

### Authentication
```
POST /api/auth/register
POST /api/auth/login
```

### Consultation
```
POST /api/consultation/start
POST /api/consultation/chat
POST /api/consultation/analyze
POST /api/consultation/plan
POST /api/consultation/complete
```

## 🗄️ Database

Using SQLite for development (medtwin.db)

Tables:
- users
- consultations
- tickets

## 🔑 Environment Variables

Required in `.env`:
- `DEEPSEEK_API_KEY` - Your DeepSeek API key
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT secret key

## 📝 Notes

- CORS is enabled for all origins (development only)
- Database is created automatically on first run
- Default port: 5000

## 🐛 Troubleshooting

If you get import errors, make sure:
1. Virtual environment is activated
2. All dependencies are installed
3. You're in the correct directory

---

**For complete setup guide, see: `HOW_TO_RUN_WEBSITE_WITH_AGENTS.md`**
