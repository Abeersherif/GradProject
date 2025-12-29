# =============================================================================
# MEDTWIN DEPLOYMENT TO RENDER + VERCEL
# Complete Guide for Deploying React Frontend + Flask Backend + All Agents
# =============================================================================

# STEP 1: PREPARE BACKEND
# ------------------------
Write-Host "=== STEP 1: Preparing Backend for Deployment ===" -ForegroundColor Green

# Navigate to backend
cd c:\Users\Administrator\Desktop\Agents\gp-backend

# Check requirements.txt
if (Test-Path "requirements.txt") {
    Write-Host "✓ requirements.txt found" -ForegroundColor Green
} else {
    Write-Host "✗ requirements.txt NOT found - deployment will fail!" -ForegroundColor Red
}

# Check .env.example
if (Test-Path ".env.example") {
    Write-Host "✓ .env.example found" -ForegroundColor Green
} else {
    Write-Host "✗ .env.example NOT found" -ForegroundColor Yellow
}

# STEP 2: PREPARE FRONTEND
# -------------------------
Write-Host "`n=== STEP 2: Preparing Frontend for Deployment ===" -ForegroundColor Green

cd c:\Users\Administrator\Desktop\Agents\medtwin-react

# Check package.json
if (Test-Path "package.json") {
    Write-Host "✓ package.json found" -ForegroundColor Green
} else {
    Write-Host "✗ package.json NOT found - deployment will fail!" -ForegroundColor Red
}

# Check .env.production.example
if (Test-Path ".env.production.example") {
    Write-Host "✓ .env.production.example found" -ForegroundColor Green
    Write-Host "  Remember to create .env.production before deploying to Vercel" -ForegroundColor Yellow
} else {
    Write-Host "✗ .env.production.example NOT found" -ForegroundColor Yellow
}

# STEP 3: GIT PREPARATION
# -----------------------
Write-Host "`n=== STEP 3: Git Repository Setup ===" -ForegroundColor Green

cd c:\Users\Administrator\Desktop\Agents

# Check if git is initialized
if (Test-Path ".git") {
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "! Git not initialized. Initializing..." -ForegroundColor Yellow
    git init
    git branch -M main
}

# Show git status
Write-Host "`nCurrent git status:" -ForegroundColor Cyan
git status --short

# STEP 4: DEPLOYMENT INSTRUCTIONS
# --------------------------------
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT READY! Follow these steps:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n📦 STEP 1: PUSH TO GITHUB" -ForegroundColor Green
Write-Host "  1. Create a new repository on GitHub" -ForegroundColor White
Write-Host "  2. Run these commands:" -ForegroundColor White
Write-Host "     git add ." -ForegroundColor Yellow
Write-Host "     git commit -m 'Prepare MedTwin for deployment'" -ForegroundColor Yellow
Write-Host "     git remote add origin https://github.com/YOUR_USERNAME/medtwin.git" -ForegroundColor Yellow
Write-Host "     git push -u origin main" -ForegroundColor Yellow

Write-Host "`n🖥️  STEP 2: DEPLOY BACKEND TO RENDER" -ForegroundColor Green
Write-Host "  1. Go to https://render.com and sign up with GitHub" -ForegroundColor White
Write-Host "  2. Click 'New +' → 'Web Service'" -ForegroundColor White
Write-Host "  3. Connect your GitHub repository" -ForegroundColor White
Write-Host "  4. Configure:" -ForegroundColor White
Write-Host "     - Name: medtwin-backend" -ForegroundColor Yellow
Write-Host "     - Root Directory: gp-backend" -ForegroundColor Yellow
Write-Host "     - Runtime: Python 3" -ForegroundColor Yellow
Write-Host "     - Build Command: pip install -r requirements.txt" -ForegroundColor Yellow
Write-Host "     - Start Command: gunicorn app:app --bind 0.0.0.0:`$PORT" -ForegroundColor Yellow
Write-Host "  5. Add Environment Variables:" -ForegroundColor White
Write-Host "     - DEEPSEEK_API_KEY=your_api_key" -ForegroundColor Yellow
Write-Host "     - FLASK_ENV=production" -ForegroundColor Yellow
Write-Host "     - PYTHON_VERSION=3.11.0" -ForegroundColor Yellow
Write-Host "  6. Click 'Create Web Service'" -ForegroundColor White
Write-Host "  7. Wait for deployment and COPY YOUR BACKEND URL" -ForegroundColor White

Write-Host "`n🌐 STEP 3: DEPLOY FRONTEND TO VERCEL" -ForegroundColor Green
Write-Host "  Option A - Using Vercel CLI:" -ForegroundColor White
Write-Host "    1. Install Vercel CLI: npm install -g vercel" -ForegroundColor Yellow
Write-Host "    2. Navigate to frontend: cd medtwin-react" -ForegroundColor Yellow
Write-Host "    3. Deploy: vercel --prod" -ForegroundColor Yellow
Write-Host "    4. Set environment variable VITE_API_URL to your backend URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Option B - Using Vercel Dashboard:" -ForegroundColor White
Write-Host "    1. Go to https://vercel.com and sign up with GitHub" -ForegroundColor Yellow
Write-Host "    2. Click 'New Project' and import your repository" -ForegroundColor Yellow
Write-Host "    3. Configure:" -ForegroundColor Yellow
Write-Host "       - Framework Preset: Vite" -ForegroundColor Yellow
Write-Host "       - Root Directory: medtwin-react" -ForegroundColor Yellow
Write-Host "       - Build Command: npm run build" -ForegroundColor Yellow
Write-Host "       - Output Directory: dist" -ForegroundColor Yellow
Write-Host "    4. Add environment variable:" -ForegroundColor Yellow
Write-Host "       - VITE_API_URL = https://medtwin-backend-xxxx.onrender.com" -ForegroundColor Yellow
Write-Host "    5. Click 'Deploy'" -ForegroundColor Yellow

Write-Host "`n🔄 STEP 4: UPDATE CORS" -ForegroundColor Green
Write-Host "  1. After frontend is deployed, copy its URL" -ForegroundColor White
Write-Host "  2. Go to Render → Your Backend Service → Environment" -ForegroundColor White
Write-Host "  3. Add environment variable:" -ForegroundColor White
Write-Host "     - FRONTEND_URL = https://your-frontend-url.vercel.app" -ForegroundColor Yellow
Write-Host "  4. Backend will automatically redeploy" -ForegroundColor White

Write-Host "`n✅ STEP 5: TEST YOUR DEPLOYMENT" -ForegroundColor Green
Write-Host "  1. Visit your frontend URL" -ForegroundColor White
Write-Host "  2. Test login/registration" -ForegroundColor White
Write-Host "  3. Test digital twin visualization" -ForegroundColor White
Write-Host "  4. Verify 3D models load" -ForegroundColor White
Write-Host "  5. Test all agents" -ForegroundColor White

Write-Host "`n🔐 OPTIONAL: GOOGLE CALENDAR SETUP" -ForegroundColor Green
Write-Host "  1. Go to Google Cloud Console" -ForegroundColor White
Write-Host "  2. Update OAuth redirect URIs to include:" -ForegroundColor White
Write-Host "     - https://medtwin-backend-xxxx.onrender.com/oauth2callback" -ForegroundColor Yellow
Write-Host "  3. In Render, add Secret File:" -ForegroundColor White
Write-Host "     - Filename: credentials.json" -ForegroundColor Yellow
Write-Host "     - Content: [your credentials.json content]" -ForegroundColor Yellow

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "NEED DETAILED HELP?" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "For complete step-by-step instructions with screenshots:"
Write-Host "  - Render docs: https://render.com/docs" -ForegroundColor Blue
Write-Host "  - Vercel docs: https://vercel.com/docs" -ForegroundColor Blue
Write-Host "`n"

Write-Host "💰 COST ESTIMATE:" -ForegroundColor Green
Write-Host "  - Free Tier: `$0/month (with sleep on inactivity)" -ForegroundColor White
Write-Host "  - Production: `$7-27/month (no sleep, better performance)" -ForegroundColor White

Write-Host "`n🎉 Ready to deploy! Good luck!" -ForegroundColor Green
