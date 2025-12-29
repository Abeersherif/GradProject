"""
Real Google Calendar Integration for Streamlit
This module connects to the Flask backend for actual Google Calendar functionality
"""

import requests
import webbrowser
from typing import Dict, Any

class StreamlitGoogleCalendar:
    """
    Connects Streamlit app to Flask backend for Google Calendar integration
    """
    
    def __init__(self, backend_url: str = "http://localhost:5000"):
        self.backend_url = backend_url
        self.access_token = None
    
    def set_access_token(self, token: str):
        """Set JWT access token for API calls"""
        self.access_token = token
    
    def get_auth_url(self) -> Dict[str, Any]:
        """
        Get Google Calendar authorization URL from backend
        
        Returns:
            Dictionary with authorization URL or error
        """
        try:
            headers = {}
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            response = requests.get(
                f'{self.backend_url}/api/notification/calendar/connect',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'authorization_url': data.get('authorization_url'),
                    'state': data.get('state')
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to get authorization URL',
                    'details': response.text
                }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Backend not running',
                'message': 'Please start the Flask backend: python gp-backend/app.py'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def connect_calendar(self, user_email: str) -> Dict[str, Any]:
        """
        Initiate Google Calendar connection
        
        Args:
            user_email: User's email address
            
        Returns:
            Status dictionary
        """
        result = self.get_auth_url()
        
        if result.get('success'):
            # Open browser for OAuth
            auth_url = result['authorization_url']
            webbrowser.open(auth_url)
            
            return {
                'success': True,
                'message': 'Please authorize in the browser window that just opened',
                'auth_url': auth_url
            }
        else:
            return result
    
    def check_connection_status(self) -> Dict[str, Any]:
        """
        Check if Google Calendar is connected
        
        Returns:
            Connection status
        """
        try:
            headers = {}
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            response = requests.get(
                f'{self.backend_url}/api/notification/calendar/status',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'connected': data.get('connected', False),
                    'message': data.get('message', '')
                }
            else:
                return {
                    'success': False,
                    'connected': False,
                    'error': 'Failed to check status'
                }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'connected': False,
                'error': 'Backend not running'
            }
        except Exception as e:
            return {
                'success': False,
                'connected': False,
                'error': str(e)
            }
    
    def create_medication_reminder(
        self,
        medication: Dict[str, Any],
        num_days: int = 30
    ) -> Dict[str, Any]:
        """
        Create Google Calendar reminder for medication
        
        Args:
            medication: Medication details
            num_days: Number of days to create reminders for
            
        Returns:
            Creation status
        """
        try:
            headers = {'Content-Type': 'application/json'}
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            response = requests.post(
                f'{self.backend_url}/api/notification/medication/add-reminders',
                headers=headers,
                json={
                    'medication': medication,
                    'num_days': num_days
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    'success': True,
                    'message': data.get('message', 'Reminders created'),
                    'events': data.get('events', [])
                }
            else:
                data = response.json()
                return {
                    'success': False,
                    'error': data.get('error', 'Failed to create reminders'),
                    'message': data.get('message', '')
                }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Backend not running',
                'message': 'Please start the Flask backend'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
google_calendar = StreamlitGoogleCalendar()
