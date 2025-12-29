import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('DEEPSEEK_API_KEY')
print(f"API Key exists: {bool(api_key)}")
print(f"API Key length: {len(api_key) if api_key else 0}")

if api_key:
    print(f"API Key starts with: {api_key[:10]}...")
    
    # Try to initialize the agent
    try:
        from agents import get_llm, get_symptom_agent
        print("Importing agents...")
        
        llm = get_llm()
        print(f"LLM initialized: {llm}")
        
        agent = get_symptom_agent()
        print(f"Symptom agent initialized: {agent}")
        
        # Try a test call
        response = agent.start_interview("I have a headache")
        print(f"Test response: {response[:100]}...")
        
    except Exception as e:
        print(f"Error initializing agent: {e}")
        import traceback
        traceback.print_exc()
else:
    print("ERROR: DEEPSEEK_API_KEY not found in .env file!")
