# 🏥 MedTwin React - Luxury Healthcare Platform

A premium, AI-powered digital twin healthcare platform built with React + Vite, featuring 9 specialized AI agents for comprehensive patient care.

## ✨ Features

### **9 Specialized AI Agents**
1. **Diagnostic Agent** - Intelligent symptom interviews
2. **Analysis & Simulation Agent** - Clinical standards evaluation
3. **Planner Agent** - Personalized care plans
4. **Prediction & Cognitive Agent** - Long-term risk forecasting
5. **Triage & Safety Agent** - Urgency assessment
6. **Treatment & Notifier Agent** - Medication tracking
7. **Doctor Assistant Agent** - Clinical decision support
8. **Lab Results Agent** - Report interpretation
9. **Coordinator Agent** - Workflow orchestration

### **Luxury Design System**
- Premium color palette (Deep Plum, Rose Gold, Champagne Gold)
- Glassmorphism effects
- Smooth animations and transitions
- Responsive design
- Custom components

### **User Roles**
- **Patients**: Health monitoring, AI consultations, medication tracking
- **Doctors**: Patient management, AI assistance, clinical insights

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will run on `http://localhost:3000`

## 📁 Project Structure

```
medtwin-react/
├── src/
│   ├── components/          # Reusable React components
│   │   └── AnimatedBackground.jsx
│   ├── pages/              # Page components
│   │   ├── LandingPage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── SignUpPage.jsx
│   │   ├── PatientDashboard.jsx
│   │   ├── DoctorDashboard.jsx
│   │   ├── ConsultationPage.jsx
│   │   ├── MedicationsPage.jsx
│   │   ├── LabResultsPage.jsx
│   │   └── ProfilePage.jsx
│   ├── services/           # API services
│   │   └── api.js         # Agent & backend integration
│   ├── config/            # Configuration files
│   │   └── agents.js      # AI agents configuration
│   ├── utils/             # Utility functions
│   ├── App.jsx            # Main app component
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── index.html            # HTML template
├── vite.config.js        # Vite configuration
└── package.json          # Dependencies
```

## 🔌 Backend Integration

### Environment Variables

Create a `.env` file in the root:

```env
VITE_API_URL=http://localhost:5000/api
```

### API Endpoints

The app connects to your backend at the following endpoints:

**Authentication:**
- `POST /api/auth/login`
- `POST /api/auth/signup`

**AI Agents:**
- `POST /api/agents/diagnostic/start`
- `POST /api/agents/diagnostic/continue`
- `POST /api/agents/analysis/analyze`
- `GET /api/agents/prediction/:patientId`
- `POST /api/agents/planner/create-plan`
- `GET /api/agents/triage/:consultationId`
- `GET /api/agents/notifier/medications/:patientId`
- `POST /api/agents/notifier/adherence`
- `POST /api/agents/lab-results/interpret`
- `GET /api/agents/doctor-assistant/summary/:patientId`
- `GET /api/agents/coordinator/ticket/:consultationId`

**Patient:**
- `GET /api/patient/dashboard`
- `GET /api/patient/consultations`
- `GET /api/patient/profile`
- `PUT /api/patient/profile`

**Doctor:**
- `GET /api/doctor/dashboard`
- `GET /api/doctor/queue`
- `GET /api/doctor/patients/:patientId`
- `POST /api/doctor/approve/:ticketId`

## 🎨 Design System

### Color Palette

```css
--plum-deep: #2D1B3D        /* Primary dark */
--purple-royal: #6B46C1     /* Accent purple */
--rose-gold: #E8B4B8        /* Warm accent */
--champagne: #D4AF37        /* Gold accent */
--cream: #F5F1E8            /* Light text */
--sage: #A8B5A0             /* Success/health */
--coral: #F4A89F            /* Warning/urgent */
```

### Typography

- **Headings**: Outfit (Google Fonts)
- **Body**: Inter (Google Fonts)

## 🔐 Authentication

The app uses JWT tokens stored in localStorage:
- Token stored on login/signup
- Automatically added to API requests
- Redirects to login on 401 errors

## 📱 Pages

### Public Pages
- **Landing Page** (`/`) - Hero, features, how it works
- **Login** (`/login`) - User authentication
- **Sign Up** (`/signup`) - Multi-step registration

### Patient Pages
- **Dashboard** (`/patient/dashboard`) - Health overview
- **Consultation** (`/patient/consultation`) - AI symptom interview
- **Medications** (`/patient/medications`) - Medication tracking
- **Lab Results** (`/patient/lab-results`) - Test results
- **Profile** (`/patient/profile`) - User settings

### Doctor Pages
- **Dashboard** (`/doctor/dashboard`) - Patient queue
- **Patient Details** (`/doctor/patients/:id`) - Patient review
- **Profile** (`/doctor/profile`) - Doctor settings

## 🤖 Using AI Agents

Import and use the agent service:

```javascript
import { agentService } from './services/api'

// Start a consultation
const consultation = await agentService.startConsultation("I have chest pain")

// Continue consultation
const response = await agentService.continueConsultation(
  consultation.id, 
  "Yes, for 2 days"
)

// Get analysis
const analysis = await agentService.performAnalysis(consultation.id)

// Create care plan
const plan = await agentService.createCarePlan(consultation.id)
```

## 🛠️ Development

### Adding a New Page

1. Create component in `src/pages/`
2. Add route in `src/App.jsx`
3. Import in navigation components

### Adding a New Agent Feature

1. Update `src/config/agents.js`
2. Add API method in `src/services/api.js`
3. Create UI component to interact with agent

## 📦 Building for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

## 🚀 Deployment

The app can be deployed to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Any static hosting service

## 📄 License

Private - MedTwin Healthcare Platform

## 👥 Team

Built with ❤️ for intelligent healthcare

---

**Need help?** Check the backend integration guide or contact the development team.
