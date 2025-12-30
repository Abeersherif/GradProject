# MedTwin - Digital Twin System

This project is a Digital Twin system for Type 2 Diabetes management, featuring a 3D visualization and AI-powered analysis.

## Prerequisites

- Python 3.8+
- [Optional] DeepSeek API Key for AI features

## Setup

1.  **Navigate to the project directory:**
    ```bash
    cd "d:/Year 4 semster 1/GRAD PROJECT/medtwin"
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    To enable the AI agents, set your DeepSeek API key:
    ```bash
    # Windows (PowerShell):
    $env:DEEPSEEK_API_KEY="your-api-key-here"
    
    # Windows (CMD):
    set DEEPSEEK_API_KEY=your-api-key-here
    
    # Mac/Linux:
    export DEEPSEEK_API_KEY=your-api-key-here
    ```

## Running the Application

1.  **Start the Backend Server:**
    Run the following command to start the FastAPI server:
    ```bash
    uvicorn api:app --reload
    ```

2.  **Access the Application:**
    Open your web browser and navigate to:
    [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Features
- **3D Visualization:** View patient organ health.
- **Cognitive Brain:** AI-powered health analysis (requires API key).
- **Simulation:** Project future health states based on lifestyle changes.

## Troubleshooting
- If `assets` are missing, 3D models won't load. Ensure the `assets` folder is present.
- If AI features fail, check the console for API key warnings.