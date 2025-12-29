env_content = """FLASK_ENV=development
SECRET_KEY=medtwin-secret-key
JWT_SECRET_KEY=medtwin-jwt-secret
DATABASE_URL=sqlite:///medtwin.db
DEEPSEEK_API_KEY=sk-9281fc022631d4fb483c45a4bf4e9e4e7
PORT=5000
"""
with open('gp-backend/.env', 'w', encoding='utf-8') as f:
    f.write(env_content)
print("Updated .env successfully")
