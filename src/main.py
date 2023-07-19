import os
import datetime
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from config import MY_EMAIL, TWILIO_ACCOUNT_ID, TWILIO_AUTH_TOKEN, MY_NUMBER, MY_TWILIO_NUMBER, CUSTOM_MESSAGE, REPEAT_MESSAGE_VALUE
from twilio.rest import Client


CREDENTIALS_FILE_PATH = '../credentials.json'
CACHED_EVENTS_FILE_PATH = "events.json"
# read only access
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MAX_EVENTS_RESULTS = 10
LAST_FETCH_TIME = None
FETCH_PERIOD = 10 * 60 * 1000

TIME_TO_CALL_BEFORE_EVENT = {
    "value": 1,
    "unit":"minutes"
}

def call(event):
    account_sid = TWILIO_ACCOUNT_ID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    custom_message = CUSTOM_MESSAGE.format(event["summary"])
    twiml = f'<Response><Say loop="{REPEAT_MESSAGE_VALUE}">{custom_message}</Say></Response>'
    call = client.calls.create(twiml=twiml,to= MY_NUMBER,from_=MY_TWILIO_NUMBER)

def get_time_difference_per_unit(time_diff_sec):
    unit = TIME_TO_CALL_BEFORE_EVENT['unit']
    return {
        "seconds": time_diff_sec,
        "minutes": time_diff_sec / 60,
        "hours": time_diff_sec / 60 /60,
        "days": time_diff_sec / 60 / 60 / 24
    }[unit]


def get_calendar_events(user_email):
    global LAST_FETCH_TIME
    should_fetch = (LAST_FETCH_TIME is None or time.time() - LAST_FETCH_TIME > FETCH_PERIOD)
    print('should_fetch: ',should_fetch)
    events_result = None
    if not should_fetch and os.path.exists(CACHED_EVENTS_FILE_PATH):
        with open(CACHED_EVENTS_FILE_PATH, "r") as file:
            json_data = file.read()
            events_result = json.loads(json_data)
            
        
    if(should_fetch or not events_result):
        LAST_FETCH_TIME = time.time()
        print("fetching")
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
        
        json_data = json.dumps(events_result)

        with open(CACHED_EVENTS_FILE_PATH, "w") as file:
            file.write(json_data)


    events = events_result.get('items', [])
    if events:
        for event in events:
                event_time = event['start']['dateTime']
                event_timestamp = datetime.datetime.fromisoformat(event_time[:-1]).timestamp()
                current_datetime_timestamp = datetime.datetime.utcnow().timestamp()
                time_difference_in_seconds = (event_timestamp - current_datetime_timestamp)
                time_difference = get_time_difference_per_unit(time_difference_in_seconds)
                if (time_difference <= 1 and time_difference > 0):
                    call(event)
                    return

    

if __name__ == '__main__':
    get_calendar_events(MY_EMAIL)
 