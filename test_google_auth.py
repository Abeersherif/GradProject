"""
Test Google Calendar Authentication
Quick test to see if credentials.json works
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def test_auth():
    """Test Google Calendar authentication"""
    
    print("=" * 50)
    print("Testing Google Calendar Authentication")
    print("=" * 50)
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ ERROR: credentials.json not found!")
        print(f"   Looking in: {os.path.abspath('credentials.json')}")
        return
    
    print("✅ credentials.json found")
    print(f"   Location: {os.path.abspath('credentials.json')}")
    
    try:
        # Try to create OAuth flow
        print("\n📝 Creating OAuth flow...")
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',
            SCOPES
        )
        
        print("✅ OAuth flow created successfully")
        
        # Try to run local server
        print("\n🌐 Starting local OAuth server...")
        print("   A browser window will open...")
        print("   Please sign in and authorize the app")
        
        creds = flow.run_local_server(
            port=0,
            prompt='consent',
            success_message='✅ Authentication successful! You can close this window.',
            open_browser=True
        )
        
        print("\n✅ Authentication successful!")
        print(f"   Access token obtained: {creds.token[:20]}...")
        
        # Try to access calendar
        print("\n📅 Testing Calendar API access...")
        service = build('calendar', 'v3', credentials=creds)
        
        # Get calendar list
        calendars = service.calendarList().list().execute()
        
        print(f"✅ Calendar API works! Found {len(calendars.get('items', []))} calendars")
        
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! Google Calendar is working!")
        print("=" * 50)
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: File not found - {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print("\n📋 Full error details:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth()
