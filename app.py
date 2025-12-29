"""
MedTwin Streamlit Web Interface
Powered by DeepSeek AI
"""

import streamlit as st
import os
from medtwin_agents import initialize_deepseek, SymptomQAAgent, AnalysisAgent, PlanningAgent, CoordinatorAgent, NotifierAgent, PredictionAgent, LabResultsAgent
from real_google_calendar import real_calendar

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MedTwin AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .analysis-box {
        background-color: #e8f4f8;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# TITLE
# ============================================================

st.markdown('<div class="main-header">🏥 MedTwin - AI Medical Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by DeepSeek AI | Advanced Medical Interview System</div>', unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "qa_agent" not in st.session_state:
    st.session_state.qa_agent = None

if "analysis_agent" not in st.session_state:
    st.session_state.analysis_agent = None

if "planning_agent" not in st.session_state:
    st.session_state.planning_agent = None

if "coordinator_agent" not in st.session_state:
    st.session_state.coordinator_agent = None

if "notifier_agent" not in st.session_state:
    st.session_state.notifier_agent = None

if "prediction_agent" not in st.session_state:
    st.session_state.prediction_agent = None

if "lab_agent" not in st.session_state:
    st.session_state.lab_agent = None

if "medications" not in st.session_state:
    st.session_state.medications = []

if "use_coordinator" not in st.session_state:
    st.session_state.use_coordinator = False

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "interview_complete" not in st.session_state:
    st.session_state.interview_complete = False

if "llm_ready" not in st.session_state:
    st.session_state.llm_ready = False

# ============================================================
# SIDEBAR - API KEY CONFIGURATION
# ============================================================

with st.sidebar:
    st.title("Navigation")
    app_mode = st.radio("Choose Mode", ["Medical Interview", "Lab Analysis"], label_visibility="collapsed")
    st.divider()

    st.header("⚙️ Configuration")
    
    # API Key inputs
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="sk-...",
        help="Get your API key from https://platform.deepseek.com",
        value=os.environ.get("DEEPSEEK_API_KEY", "")
    )
    
    google_api_key = st.text_input(
        "Google Gemini API Key (for Images)",
        type="password",
        placeholder="AIza...",
        help="Required for analyzing images (Get at aistudio.google.com)",
        value=os.environ.get("GOOGLE_API_KEY", "")
    )
    
    # Debug Tool for User
    if google_api_key and st.sidebar.button("🕵️ Check Google API Access"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_api_key)
            
            st.sidebar.info("Querying available models...")
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m.name)
            
            if models:
                st.sidebar.success(f"✅ Found {len(models)} models!")
                st.sidebar.code("\n".join(models), language="text")
            else:
                st.sidebar.warning("⚠️ Access confirmed, but no 'generateContent' models found.")
                
        except Exception as e:
            st.sidebar.error(f"❌ API Error: {e}")

    if st.button("Initialize AI", type="primary"):
        if api_key and api_key.startswith("sk-"):
            try:
                with st.spinner("Initializing DeepSeek AI..."):
                    llm = initialize_deepseek(api_key)
                    # Set ENV for agents that might need it
                    os.environ["DEEPSEEK_API_KEY"] = api_key
                    if google_api_key:
                        os.environ["GOOGLE_API_KEY"] = google_api_key
                        
                    st.session_state.qa_agent = SymptomQAAgent(llm)
                    # ... (rest of init) ...
                    st.session_state.analysis_agent = AnalysisAgent(llm)
                    st.session_state.planning_agent = PlanningAgent(llm)
                    st.session_state.coordinator_agent = CoordinatorAgent(llm)
                    st.session_state.notifier_agent = NotifierAgent(llm)
                    st.session_state.prediction_agent = PredictionAgent(llm)
                    st.session_state.lab_agent = LabResultsAgent(llm)
                    st.session_state.llm_ready = True
                st.success("✅ AI initialized successfully! All 5 agents ready (including Notifier).")
            except Exception as e:
                st.error(f"❌ Failed to initialize: {e}")
        else:
            st.warning("⚠️ Please enter a valid API key (starts with 'sk-')")
    
    st.divider()
    
    # Status
    st.header("📊 Status")
    if st.session_state.llm_ready:
        st.success("🟢 AI Ready")
    else:
        st.error("🔴 AI Not Initialized")
    
    if st.session_state.interview_started:
        st.info(f"📝 Interview: In Progress")
    else:
        st.info("📝 Interview: Not Started")
    
    st.metric("Messages", len(st.session_state.messages))
    
    st.divider()
    
    # Agent Mode Selection
    st.header("🤖 Agent Mode")
    use_coordinator = st.checkbox(
        "Use Coordinator Agent",
        value=st.session_state.use_coordinator,
        help="Coordinator orchestrates all agents automatically"
    )
    if use_coordinator != st.session_state.use_coordinator:
        st.session_state.use_coordinator = use_coordinator
    
    if st.session_state.use_coordinator:
        st.info("🔄 Coordinator Mode: All agents work together")
    else:
        st.info("👤 Manual Mode: Individual agents")
    
    st.divider()
    
    # Actions
    st.header("🎯 Actions")
    
    if st.button("🔄 New Interview"):
        if st.session_state.llm_ready:
            # Reinitialize agents
            api_key_env = os.environ.get("DEEPSEEK_API_KEY")
            if api_key_env:
                llm = initialize_deepseek(api_key_env)
                st.session_state.qa_agent = SymptomQAAgent(llm)
                st.session_state.analysis_agent = AnalysisAgent(llm)
                st.session_state.planning_agent = PlanningAgent(llm)
                st.session_state.coordinator_agent = CoordinatorAgent(llm)
                st.session_state.notifier_agent = NotifierAgent(llm)
                st.session_state.prediction_agent = PredictionAgent(llm)
                st.session_state.lab_agent = LabResultsAgent(llm)
            st.session_state.messages = []
            st.session_state.interview_started = False
            st.session_state.interview_complete = False
            st.rerun()
        else:
            st.warning("Please initialize AI first!")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Info
    st.header("ℹ️ About")
    st.info("""
    **MedTwin** is an AI-powered medical assistant that helps with:
    - 🩺 Diabetes
    - 💊 Hypertension
    - ❤️ Heart Disease
    - 🫁 COPD
    
    The system conducts intelligent interviews and provides medical recommendations.
    """)
    
    st.divider()
    
    # Resources
    st.header("🔗 Resources")
    st.markdown("[DeepSeek Platform](https://platform.deepseek.com)")
    st.markdown("[Get API Key](https://platform.deepseek.com)")
    st.markdown("[Documentation](https://platform.deepseek.com/api-docs)")
    
    st.divider()
    
    # ============================================================
    # MEDICATION MANAGEMENT IN SIDEBAR
    # ============================================================
    
    st.header("💊 Medication Manager")
    
    if st.session_state.llm_ready:
        # Patient Email for Google Calendar
        if "patient_email" not in st.session_state:
            st.session_state.patient_email = ""
        
        if "calendar_connected" not in st.session_state:
            st.session_state.calendar_connected = False
        
        # Email input
        patient_email = st.text_input(
            "📧 Your Email",
            value=st.session_state.patient_email,
            placeholder="patient@gmail.com",
            help="Enter your email to connect Google Calendar for automatic reminders"
        )
        
        if patient_email != st.session_state.patient_email:
            st.session_state.patient_email = patient_email
        
        # Google Calendar Connection Status
        if st.session_state.patient_email:
            # Check if already connected
            is_connected = real_calendar.is_connected(st.session_state.patient_email)
            
            if is_connected:
                st.session_state.calendar_connected = True
                st.success("✅ Google Calendar Connected")
                st.caption(f"Reminders will be sent to: {st.session_state.patient_email}")
            else:
                st.session_state.calendar_connected = False
                
                if st.button("🔗 Connect Google Calendar", type="secondary"):
                    with st.spinner("Opening Google authentication..."):
                        # Real OAuth authentication
                        result = real_calendar.authenticate(st.session_state.patient_email)
                        
                        if result.get('success'):
                            st.session_state.calendar_connected = True
                            st.success("✅ Google Calendar connected successfully!")
                            st.success(result.get('message', ''))
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {result.get('message', 'Connection failed')}")
                            if 'credentials.json not found' in result.get('error', ''):
                                st.warning("""
                                **Setup Required:**
                                1. Go to [Google Cloud Console](https://console.cloud.google.com)
                                2. Create a project and enable Google Calendar API
                                3. Create OAuth credentials
                                4. Download credentials.json
                                5. Place it in: `C:\\Users\\Administrator\\Desktop\\Agents\\credentials.json`
                                """)
                
                st.caption("⚠️ Click to enable automatic reminders")
        
        st.divider()
        
        # Add Medication Form
        with st.expander("➕ Add Medication", expanded=False):
            with st.form("sidebar_medication_form", clear_on_submit=True):
                med_name = st.text_input("Medication Name*", placeholder="e.g., Aspirin")
                
                col1, col2 = st.columns(2)
                with col1:
                    med_dosage = st.text_input("Dosage*", placeholder="e.g., 81mg")
                with col2:
                    med_frequency = st.selectbox(
                        "Frequency*",
                        ["Once daily", "Twice daily", "Three times daily", "As needed"]
                    )
                
                med_time1 = st.time_input("Dose time", value=None, key="sidebar_time1")
                med_instructions = st.text_area(
                    "Instructions",
                    placeholder="e.g., Take with food",
                    height=60
                )
                
                submitted = st.form_submit_button("💾 Save Medication", type="primary")
                
                if submitted:
                    if med_name and med_dosage and med_frequency:
                        # Collect timing
                        timing = []
                        if med_time1:
                            timing.append(med_time1.strftime("%H:%M"))
                        
                        medication_data = {
                            "name": med_name,
                            "dosage": med_dosage,
                            "frequency": med_frequency,
                            "timing": timing,
                            "instructions": med_instructions,
                            "patient_email": st.session_state.patient_email
                        }
                        
                        # Add to notifier agent
                        result = st.session_state.notifier_agent.add_medication(medication_data)
                        
                        # Add to session state
                        st.session_state.medications.append(medication_data)
                        
                        st.success(f"✅ {result['message']}")
                        
                        # Auto-create REAL Google Calendar reminder if connected
                        if st.session_state.calendar_connected and st.session_state.patient_email and timing:
                            with st.spinner("Creating Google Calendar events..."):
                                # Create REAL calendar events
                                calendar_result = real_calendar.create_medication_reminder(
                                    st.session_state.patient_email,
                                    medication_data,
                                    num_days=30
                                )
                                
                                if calendar_result.get('success'):
                                    events = calendar_result.get('events', [])
                                    st.success(f"📅 {calendar_result['message']}")
                                    st.success(f"✅ Created {len(events)} recurring reminder(s) in Google Calendar!")
                                    st.info(f"💡 You'll receive notifications at: {', '.join(timing)}")
                                    st.info("📧 Email reminders: 30 minutes before")
                                    st.info("📱 Phone popups: 10 minutes before")
                                    
                                    # Show event links
                                    for event in events:
                                        if event.get('link'):
                                            st.caption(f"🔗 [View {event['time']} reminder in calendar]({event['link']})")
                                else:
                                    st.warning(f"⚠️ {calendar_result.get('message', 'Failed to create calendar events')}")
                                    if not real_calendar.is_connected(st.session_state.patient_email):
                                        st.error("Please reconnect Google Calendar")
                        
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("⚠️ Please fill in all required fields")
        
        # Display Current Medications
        if st.session_state.medications:
            st.markdown(f"**📋 Medications ({len(st.session_state.medications)})**")
            
            for idx, med in enumerate(st.session_state.medications, 1):
                with st.container():
                    st.markdown(f"**{idx}. {med['name']}**")
                    st.caption(f"💊 {med['dosage']} - {med['frequency']}")
                    if med.get('timing'):
                        st.caption(f"🕐 {', '.join(med['timing'])}")
                    if med.get('instructions'):
                        st.caption(f"📝 {med['instructions']}")
                    
                    # Show calendar status
                    if st.session_state.calendar_connected:
                        st.caption("✅ Calendar reminder active")
                    
                    st.markdown("---")
            
            # Generate Schedule Button
            if st.button("📅 Generate Full Schedule", type="secondary"):
                with st.spinner("Creating medication schedule..."):
                    schedule = st.session_state.notifier_agent.create_medication_schedule(
                        st.session_state.medications
                    )
                    
                    # Display in main area
                    st.session_state.show_schedule = True
                    st.session_state.generated_schedule = schedule
                    st.rerun()
        else:
            st.info("No medications added yet")
    else:
        st.warning("⚠️ Initialize AI first to use Medication Manager")

# ============================================================
# MAIN INTERFACE LOGIC
# ============================================================

if app_mode == "Lab Analysis":
    st.header("🧪 Lab Results Analysis")
    st.info("Upload your lab report or paste the text below for AI analysis.")
    
    if not st.session_state.llm_ready:
        st.warning("⚠️ Please initialize the AI in the sidebar first.")
    else:
        # File Uploader only (No text paste tab)
        uploaded_file = st.file_uploader("Upload Lab Report (Image/PDF/Text)", type=['jpg', 'jpeg', 'png', 'pdf', 'txt'])
        
        report_text = ""
        
        if uploaded_file:
            file_type = uploaded_file.type
            
            # Image Handling
            if "image" in file_type:
                from PIL import Image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Lab Report", use_column_width=True)
                
                # Use Google Gemini for OCR
                if os.environ.get("GOOGLE_API_KEY"):
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
                        
                        # Try specific versioned models from your available list
                        models_to_try = [
                            'gemini-2.5-flash',
                            'gemini-2.5-pro',
                            'gemini-2.0-flash'
                        ]
                        
                        text = None
                        last_error = None
                        
                        for model_name in models_to_try:
                            try:
                                with st.spinner(f"Attempting to read with {model_name}..."):
                                    model = genai.GenerativeModel(model_name)
                                    response = model.generate_content([
                                        "Transcribe the medical text from this image exactly.", 
                                        image
                                    ])
                                    if response.text:
                                        text = response.text
                                        st.success(f"✅ Success using {model_name}!")
                                        break
                            except Exception as e:
                                last_error = e
                                continue
                        
                        # Fallback to LangChain if raw client fails
                        if not text:
                            try:
                                with st.spinner("Attempting fallback with LangChain..."):
                                    from langchain_google_genai import ChatGoogleGenerativeAI
                                    from langchain_core.messages import HumanMessage
                                    
                                    llm_vision = ChatGoogleGenerativeAI(
                                        model="gemini-2.5-pro",
                                        google_api_key=os.environ["GOOGLE_API_KEY"]
                                    )
                                    
                                    # Convert PIL to base64 for LangChain (if needed, but usually it handles image_url)
                                    # actually LangChain invoke can take image_url, but for local PIL...
                                    # simpler to try 1.5 flash via langchain
                                    
                                    llm_vision_flash = ChatGoogleGenerativeAI(
                                        model="gemini-2.5-flash",
                                        google_api_key=os.environ["GOOGLE_API_KEY"]
                                    )
                                    
                                    import base64
                                    from io import BytesIO
                                    buffered = BytesIO()
                                    image.save(buffered, format="JPEG")
                                    img_str = base64.b64encode(buffered.getvalue()).decode()
                                    
                                    message = HumanMessage(
                                        content=[
                                            {"type": "text", "text": "Transcribe the medical text from this image exactly."},
                                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                                        ]
                                    )
                                    
                                    response = llm_vision_flash.invoke([message])
                                    text = response.content
                                    st.success("✅ Success using LangChain Fallback!")
                            except Exception as e:
                                last_error = f"LangChain Error: {e}"
                        
                        if text and text.strip():
                            report_text = text
                            with st.expander("Show Extracted Text"):
                                st.text(report_text)
                        else:
                            st.error("❌ Failed to read image with all available Gemini models.")
                            if last_error:
                                st.error(f"Last Error: {last_error}")
                            st.info("Check your API Key and ensure you have access to Gemini Vision models.")
                            
                    except Exception as e:
                        st.error(f"❌ Gemini Error: {e}")
                else:
                    st.warning("⚠️ Google API Key missing. Please provide it in the sidebar to analyze images.")
                    st.info("Without a Google API Key, I cannot read images. Please upload a PDF or Text file, or enter the key.")

            # Text/PDF Handling
            else:
                try:
                    if file_type == "application/pdf":
                        import PyPDF2
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text()
                        report_text = text
                        st.success("✅ PDF loaded successfully!")
                    else:
                        stringio = str(uploaded_file.read(), "utf-8")
                        report_text = stringio
                        st.success("✅ Text file loaded successfully!")
                except Exception as e:
                    st.warning(f"Could not read file: {e}")
        
        # Analyze Button
        if st.button("🔍 Analyze Report", type="primary"):
            if report_text:
                with st.spinner("Analyzing lab results..."):
                    # Use the new agent
                    analysis = st.session_state.lab_agent.analyze_lab_report(report_text, "Chronic Disease Management")
                    
                    st.divider()
                    st.subheader("📋 Analysis Summary")
                    st.info(analysis.get("summary", "No summary available."))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### ⚠️ Abnormalities")
                        for item in analysis.get("abnormalities", []):
                            st.error(item)
                            
                    with col2:
                        st.markdown("### ✅ Action Items")
                        for item in analysis.get("action_items", []):
                            st.success(item)
                            
                    with st.expander("Detailed Analysis", expanded=True):
                        st.write(analysis.get("detailed_analysis", ""))
            elif uploaded_file:
                st.error("⚠️ No text could be extracted from the file to analyze.")
            else:
                st.warning("Please upload a file first.")
                
    st.stop() # Stop here so we don't show the Chat Interface

# ============================================================
# MEDICAL INTERFACE (Default)
# ============================================================

# Check if AI is ready
if not st.session_state.llm_ready:
    st.warning("⚠️ Please configure your DeepSeek API key in the sidebar to start.")
    st.info("👈 Enter your API key and click 'Initialize AI'")
    
    with st.expander("📖 How to get an API key"):
        st.markdown("""
        1. Go to [DeepSeek Platform](https://platform.deepseek.com)
        2. Sign up or log in
        3. Navigate to API Keys section
        4. Create a new API key
        5. Copy and paste it in the sidebar
        6. Click 'Initialize AI'
        """)
    
    st.stop()

# ============================================================
# MEDICATION SCHEDULE DISPLAY (if generated from sidebar)
# ============================================================

if "show_schedule" not in st.session_state:
    st.session_state.show_schedule = False

if "generated_schedule" not in st.session_state:
    st.session_state.generated_schedule = ""

if st.session_state.show_schedule and st.session_state.generated_schedule:
    st.markdown("---")
    st.markdown("### 📅 Your Medication Schedule")
    st.markdown(st.session_state.generated_schedule)
    
    if st.session_state.calendar_connected:
        st.success(f"✅ Automatic reminders are active for {st.session_state.patient_email}")
        st.info("💡 You will receive notifications via Google Calendar at the scheduled times!")
    else:
        st.warning("⚠️ Connect Google Calendar in the sidebar to receive automatic reminders")
    
    if st.button("✖️ Close Schedule"):
        st.session_state.show_schedule = False
        st.rerun()
    
    st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if not st.session_state.interview_complete:
    if prompt := st.chat_input("Describe your symptoms or answer the question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    # Start or continue interview
                    if not st.session_state.interview_started:
                        response = st.session_state.qa_agent.start_interview(prompt)
                        st.session_state.interview_started = True
                    else:
                        response = st.session_state.qa_agent.continue_interview(prompt)
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Check if interview is complete
                    if st.session_state.qa_agent.interview_complete:
                        st.session_state.interview_complete = True
                        
                        # Get analysis
                        with st.spinner("Generating medical analysis..."):
                            collected_data = st.session_state.qa_agent.get_collected_data()
                            analysis = st.session_state.analysis_agent.analyze(collected_data)
                            
                            # Display analysis
                            st.divider()
                            st.markdown("### 📊 Medical Analysis")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Condition", analysis['condition'].replace('_', ' ').title())
                            with col2:
                                severity_color = {
                                    "LOW": "🟢",
                                    "MODERATE": "🟡",
                                    "HIGH": "🟠",
                                    "CRITICAL": "🔴"
                                }
                                st.metric("Severity", f"{severity_color.get(analysis['severity'], '⚪')} {analysis['severity']}")
                            with col3:
                                if analysis.get('gold_group'):
                                    st.metric("Classification", analysis['gold_group'])
                            
                            st.markdown("### 💊 Recommendations")
                            st.markdown(f'<div class="analysis-box">{analysis["recommendations"]}</div>', unsafe_allow_html=True)
                            
                            # Generate prediction
                            with st.spinner("Generating disease prediction..."):
                                prediction = st.session_state.prediction_agent.generate_comprehensive_prediction(analysis)
                                
                                st.divider()
                                st.markdown("### 🔮 Disease Prediction & Organ Impact")
                                
                                # Worsening Prediction
                                worsening = prediction['worsening_prediction']
                                if worsening.get('worsening'):
                                    st.error(f"⚠️ Warning: Case appears to be worsening")
                                else:
                                    st.success(f"✅ Status: Case appears stable/manageable")
                                
                                st.markdown(f"**Forecast:** {worsening.get('progression_forecast')}")
                                
                                if worsening.get('risk_factors'):
                                    st.markdown("**Risk Factors:**")
                                    for risk in worsening['risk_factors']:
                                        st.markdown(f"- {risk}")
                                
                                # Organ Impact
                                st.markdown("#### 🫁 Organ Impact Assessment")
                                organs = prediction['organ_impact_prediction'].get('affected_organs', [])
                                if organs:
                                    for organ in organs:
                                        risk_color = "red" if "high" in organ.get('risk_level', '').lower() else "orange"
                                        st.markdown(f"**:{risk_color}[{organ.get('organ')}]** ({organ.get('risk_level')})")
                                        st.caption(f"{organ.get('impact_description')}")
                                else:
                                    st.info("No immediate organ impact detected.")
                            
                            # Generate treatment plan
                            with st.spinner("Creating personalized treatment plan..."):
                                plan = st.session_state.planning_agent.create_comprehensive_plan(analysis)
                                
                                st.divider()
                                st.markdown("### 📋 Treatment Plan")
                                
                                # Short-term plan
                                st.markdown("#### 🎯 Short-Term Plan (1-7 days)")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown("**Daily Actions**")
                                    for action in plan['short_term_plan']['daily_actions']:
                                        st.markdown(f"✓ {action}")
                                
                                with col2:
                                    st.markdown("**Monitoring**")
                                    for item in plan['short_term_plan']['monitoring']:
                                        st.markdown(f"📊 {item}")
                                
                                with col3:
                                    st.markdown("**⚠️ Red Flags**")
                                    for flag in plan['short_term_plan']['red_flags']:
                                        st.markdown(f"🚨 {flag}")
                                
                                # Long-term plan
                                st.markdown("#### 🎯 Long-Term Plan (1-3 months)")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown("**Lifestyle Changes**")
                                    for change in plan['long_term_plan']['lifestyle_changes']:
                                        st.markdown(f"🌱 {change}")
                                
                                with col2:
                                    st.markdown("**Follow-up Schedule**")
                                    for appt in plan['long_term_plan']['follow_up_schedule']:
                                        st.markdown(f"📅 {appt}")
                                
                                with col3:
                                    st.markdown("**Goals**")
                                    for goal in plan['long_term_plan']['goals']:
                                        st.markdown(f"🎯 {goal}")
                            
                            st.success("✅ Complete consultation finished! Click 'New Interview' in the sidebar to start another.")
                
                except Exception as e:
                    # Show detailed error information
                    st.error(f"❌ Error: {str(e)}")
                    st.error(f"Error Type: {type(e).__name__}")
                    
                    # Show more details in expander
                    with st.expander("🔍 Error Details (for debugging)"):
                        import traceback
                        st.code(traceback.format_exc())
                    
                    st.warning("💡 Common fixes:")
                    st.markdown("""
                    - Check your API key is correct
                    - Verify you have credits: https://platform.deepseek.com/billing
                    - Try clicking 'New Interview' in the sidebar
                    - Check your internet connection
                    """)
                    st.info("Please try again or start a new interview.")
else:
    st.info("✅ Interview complete! Click 'New Interview' in the sidebar to start a new consultation.")

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>⚠️ <strong>Disclaimer:</strong> This is an AI assistant for informational purposes only. 
    Always consult with a qualified healthcare professional for medical advice.</p>
    <p>Powered by DeepSeek AI | MedTwin v1.0</p>
</div>
""", unsafe_allow_html=True)
