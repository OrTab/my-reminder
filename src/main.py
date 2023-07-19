import os
import datetime
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from config import MY_EMAIL 

CREDENTIALS_FILE_PATH = '../credentials.json'
CACHED_EVENTS_FILE_PATH = "events.json"
# read only access
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MAX_EVENTS_RESULTS = 10
LAST_FETCH_TIME = None




def get_calendar_events(user_email):        
    credentials = service_account.Credentials.from_service_account_file(
          CREDENTIALS_FILE_PATH, scopes=SCOPES
        )
    service = build('calendar', 'v3', credentials=credentials)

    now = datetime.datetime.utcnow().isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=user_email,
        timeMin=now,
        maxResults=MAX_EVENTS_RESULTS,
        singleEvents=True,
        orderBy='startTime',
        timeZone='UTC'
        ).execute()
        
    events = events_result.get('items', [])
    if events:
        for event in events:
            print(event)

    

if __name__ == '__main__':
    get_calendar_events(MY_EMAIL)
 