"""
Google Calendar Integration Service
Handles automatic calendar event creation for medication reminders
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Note: These imports require installation:
# pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

class GoogleCalendarService:
    """
    Service to manage Google Calendar integration for medication reminders
    """
    
    def __init__(self):
        self.credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
        self.token_storage_path = os.path.join(os.path.dirname(__file__), '..', 'tokens')
        
        # Ensure token storage directory exists
        os.makedirs(self.token_storage_path, exist_ok=True)
    
    def get_authorization_url(self, user_email: str) -> Dict[str, str]:
        """
        Generate OAuth authorization URL for user to grant calendar access
        
        Args:
            user_email: User's email address
            
        Returns:
            Dictionary with authorization URL and state token
        """
        try:
            from google_auth_oauthlib.flow import Flow
            
            # Create flow instance
            flow = Flow.from_client_secrets_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/calendar'],
                redirect_uri='http://localhost:3000/auth/google/callback'  # Your React app callback
            )
            
            # Generate authorization URL
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                login_hint=user_email,  # Pre-fill with user's email
                prompt='consent'
            )
            
            return {
                'authorization_url': authorization_url,
                'state': state,
                'user_email': user_email
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Google Calendar credentials not configured. Please set up credentials.json'
            }
    
    def handle_oauth_callback(self, authorization_code: str, user_email: str) -> Dict[str, Any]:
        """
        Handle OAuth callback and store credentials
        
        Args:
            authorization_code: Authorization code from Google
            user_email: User's email address
            
        Returns:
            Success status and message
        """
        try:
            from google_auth_oauthlib.flow import Flow
            from google.oauth2.credentials import Credentials
            
            # Create flow instance
            flow = Flow.from_client_secrets_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/calendar'],
                redirect_uri='http://localhost:3000/auth/google/callback'
            )
            
            # Exchange authorization code for credentials
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials
            
            # Store credentials for this user
            token_file = os.path.join(self.token_storage_path, f'{user_email}.json')
            with open(token_file, 'w') as f:
                f.write(credentials.to_json())
            
            print(f"[SUCCESS] Google Calendar token saved for {user_email} at {token_file}")
            
            return {
                'success': True,
                'message': 'Google Calendar connected successfully!',
                'user_email': user_email
            }
            
        except Exception as e:
            print(f"[ERROR] OAuth Callback failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect Google Calendar'
            }
    
    def get_user_credentials(self, user_email: str):
        """
        Load stored credentials for a user
        
        Args:
            user_email: User's email address
            
        Returns:
            Google credentials object or None
        """
        try:
            from google.oauth2.credentials import Credentials
            
            token_file = os.path.join(self.token_storage_path, f'{user_email}.json')
            
            if not os.path.exists(token_file):
                return None
            
            with open(token_file, 'r') as f:
                creds_data = json.load(f)
            
            credentials = Credentials.from_authorized_user_info(creds_data)
            
            # Refresh if expired
            if credentials.expired and credentials.refresh_token:
                from google.auth.transport.requests import Request
                credentials.refresh(Request())
                
                # Save refreshed credentials
                with open(token_file, 'w') as f:
                    f.write(credentials.to_json())
            
            return credentials
            
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None
    
    def create_medication_reminders(
        self, 
        user_email: str, 
        medication: Dict[str, Any],
        num_days: int = 30
    ) -> Dict[str, Any]:
        """
        Create recurring calendar events for medication reminders
        
        Args:
            user_email: User's email address
            medication: Medication details (name, dosage, timing, etc.)
            num_days: Number of days to create reminders for
            
        Returns:
            Status of event creation
        """
        try:
            from googleapiclient.discovery import build
            
            # Get user credentials
            credentials = self.get_user_credentials(user_email)
            
            if not credentials:
                return {
                    'success': False,
                    'error': 'User not authorized. Please connect Google Calendar first.'
                }
            
            # Build calendar service
            service = build('calendar', 'v3', credentials=credentials)
            
            # Get medication details
            med_name = medication.get('name', 'Medication')
            med_dosage = medication.get('dosage', '')
            med_instructions = medication.get('instructions', 'Take as directed')
            med_timings = medication.get('timing', [])
            
            created_events = []
            
            # Create event for each dose time
            for time_str in med_timings:
                # Parse time (format: "HH:MM")
                hour, minute = map(int, time_str.split(':'))
                
                # Create start datetime (today at specified time)
                start_datetime = datetime.now().replace(
                    hour=hour, 
                    minute=minute, 
                    second=0, 
                    microsecond=0
                )
                
                # End time is 15 minutes after start
                end_datetime = start_datetime + timedelta(minutes=15)
                
                # Create event
                event = {
                    'summary': f'💊 {med_name} - {med_dosage}',
                    'description': f'{med_instructions}\n\nDosage: {med_dosage}\nMedication: {med_name}',
                    'start': {
                        'dateTime': start_datetime.isoformat(),
                        'timeZone': 'Africa/Cairo',  # Adjust to user's timezone
                    },
                    'end': {
                        'dateTime': end_datetime.isoformat(),
                        'timeZone': 'Africa/Cairo',
                    },
                    'recurrence': [
                        f'RRULE:FREQ=DAILY;COUNT={num_days}'  # Repeat daily for num_days
                    ],
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': 10},  # Popup 10 min before
                            {'method': 'email', 'minutes': 30},  # Email 30 min before
                        ],
                    },
                    'colorId': '11',  # Red color for medication reminders
                }
                
                # Insert event
                created_event = service.events().insert(
                    calendarId='primary',
                    body=event
                ).execute()
                
                created_events.append({
                    'event_id': created_event['id'],
                    'time': time_str,
                    'link': created_event.get('htmlLink')
                })
            
            return {
                'success': True,
                'message': f'Created {len(created_events)} reminder(s) for {med_name}',
                'events': created_events,
                'medication': med_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create calendar reminders'
            }
    
    def delete_medication_reminders(
        self,
        user_email: str,
        event_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Delete medication reminder events
        
        Args:
            user_email: User's email address
            event_ids: List of event IDs to delete
            
        Returns:
            Status of deletion
        """
        try:
            from googleapiclient.discovery import build
            
            credentials = self.get_user_credentials(user_email)
            
            if not credentials:
                return {
                    'success': False,
                    'error': 'User not authorized'
                }
            
            service = build('calendar', 'v3', credentials=credentials)
            
            deleted_count = 0
            for event_id in event_ids:
                try:
                    service.events().delete(
                        calendarId='primary',
                        eventId=event_id
                    ).execute()
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete event {event_id}: {e}")
            
            return {
                'success': True,
                'message': f'Deleted {deleted_count} reminder(s)',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_calendar_connection(self, user_email: str) -> Dict[str, Any]:
        """
        Check if user has connected their Google Calendar
        
        Args:
            user_email: User's email address
            
        Returns:
            Connection status
        """
        credentials = self.get_user_credentials(user_email)
        
        if credentials:
            return {
                'connected': True,
                'email': user_email,
                'message': 'Google Calendar is connected'
            }
        else:
            return {
                'connected': False,
                'email': user_email,
                'message': 'Google Calendar not connected'
            }


# Singleton instance
calendar_service = GoogleCalendarService()
