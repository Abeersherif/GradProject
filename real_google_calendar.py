"""
Real Google Calendar Integration for Streamlit
Handles OAuth authentication and calendar event creation
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Google Calendar imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes required for Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

class RealGoogleCalendar:
    """
    Real Google Calendar integration with OAuth authentication
    """
    
    def __init__(self, credentials_path: str = 'credentials.json'):
        self.credentials_path = credentials_path
        self.token_dir = Path('tokens')
        self.token_dir.mkdir(exist_ok=True)
        self.service = None
    
    def get_credentials(self, user_email: str) -> Optional[Credentials]:
        """
        Get or refresh credentials for a user
        
        Args:
            user_email: User's email address
            
        Returns:
            Google credentials or None
        """
        token_path = self.token_dir / f'{user_email.replace("@", "_at_")}.pickle'
        creds = None
        
        # Load existing token
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed credentials
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None
        
        return creds
    
    def authenticate(self, user_email: str) -> Dict[str, Any]:
        """
        Authenticate user with Google Calendar
        
        Args:
            user_email: User's email address
            
        Returns:
            Status dictionary
        """
        try:
            # Check if credentials.json exists
            if not os.path.exists(self.credentials_path):
                return {
                    'success': False,
                    'error': 'credentials.json not found',
                    'message': 'Please download credentials.json from Google Cloud Console'
                }
            
            # Run OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                SCOPES,
                redirect_uri='http://localhost:8503'
            )
            
            # Run local server for OAuth
            creds = flow.run_local_server(
                port=8503,
                prompt='consent',
                success_message='Authentication successful! You can close this window.',
                open_browser=True
            )
            
            # Save credentials
            token_path = self.token_dir / f'{user_email.replace("@", "_at_")}.pickle'
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
            
            return {
                'success': True,
                'message': f'Successfully connected Google Calendar for {user_email}',
                'email': user_email
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to authenticate with Google Calendar'
            }
    
    def is_connected(self, user_email: str) -> bool:
        """
        Check if user has valid credentials
        
        Args:
            user_email: User's email address
            
        Returns:
            True if connected, False otherwise
        """
        creds = self.get_credentials(user_email)
        return creds is not None and creds.valid
    
    def get_calendar_service(self, user_email: str):
        """
        Get Google Calendar service for user
        
        Args:
            user_email: User's email address
            
        Returns:
            Calendar service or None
        """
        creds = self.get_credentials(user_email)
        
        if not creds or not creds.valid:
            return None
        
        try:
            service = build('calendar', 'v3', credentials=creds)
            return service
        except Exception as e:
            print(f"Error building calendar service: {e}")
            return None
    
    def create_medication_reminder(
        self,
        user_email: str,
        medication: Dict[str, Any],
        num_days: int = 30
    ) -> Dict[str, Any]:
        """
        Create recurring medication reminder in Google Calendar
        
        Args:
            user_email: User's email address
            medication: Medication details
            num_days: Number of days to create reminders for
            
        Returns:
            Status dictionary with created events
        """
        try:
            service = self.get_calendar_service(user_email)
            
            if not service:
                return {
                    'success': False,
                    'error': 'Not authenticated',
                    'message': 'Please connect Google Calendar first'
                }
            
            # Get medication details
            med_name = medication.get('name', 'Medication')
            med_dosage = medication.get('dosage', '')
            med_instructions = medication.get('instructions', 'Take as directed')
            med_timings = medication.get('timing', [])
            
            if not med_timings:
                return {
                    'success': False,
                    'error': 'No timing specified',
                    'message': 'Please specify at least one dose time'
                }
            
            created_events = []
            
            # Create event for each dose time
            for time_str in med_timings:
                try:
                    # Parse time (format: "HH:MM")
                    hour, minute = map(int, time_str.split(':'))
                    
                    # Create start datetime (today at specified time)
                    start_datetime = datetime.now().replace(
                        hour=hour,
                        minute=minute,
                        second=0,
                        microsecond=0
                    )
                    
                    # If time has passed today, start tomorrow
                    if start_datetime < datetime.now():
                        start_datetime += timedelta(days=1)
                    
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
                        'colorId': '11',  # Red color for medication
                    }
                    
                    # Insert event into calendar
                    created_event = service.events().insert(
                        calendarId='primary',
                        body=event
                    ).execute()
                    
                    created_events.append({
                        'event_id': created_event['id'],
                        'time': time_str,
                        'link': created_event.get('htmlLink'),
                        'start_date': start_datetime.strftime('%Y-%m-%d')
                    })
                    
                except Exception as e:
                    print(f"Error creating event for time {time_str}: {e}")
                    continue
            
            if created_events:
                return {
                    'success': True,
                    'message': f'Created {len(created_events)} reminder(s) for {med_name}',
                    'events': created_events,
                    'medication': med_name,
                    'email': user_email
                }
            else:
                return {
                    'success': False,
                    'error': 'No events created',
                    'message': 'Failed to create calendar events'
                }
            
        except HttpError as error:
            return {
                'success': False,
                'error': str(error),
                'message': 'Google Calendar API error'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create medication reminder'
            }
    
    def delete_medication_reminders(
        self,
        user_email: str,
        event_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Delete medication reminders from Google Calendar
        
        Args:
            user_email: User's email address
            event_ids: List of event IDs to delete
            
        Returns:
            Status dictionary
        """
        try:
            service = self.get_calendar_service(user_email)
            
            if not service:
                return {
                    'success': False,
                    'error': 'Not authenticated'
                }
            
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


# Singleton instance
real_calendar = RealGoogleCalendar()
