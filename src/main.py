import os
import datetime
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from config import (
    MY_EMAIL,
    TWILIO_ACCOUNT_ID,
    TWILIO_AUTH_TOKEN,
    MY_NUMBER,
    MY_TWILIO_NUMBER,
    CUSTOM_MESSAGE,
    REPEAT_MESSAGE_VALUE,
    SCOPES,
    MAX_EVENTS_RESULTS,
    CACHE_PERIOD,
    SLEEP_PERIOD,
    CREDENTIALS_FILE_PATH,
)
from twilio.rest import Client
from time import sleep

LAST_FETCH_TIME = None
TIME_TO_CALL_BEFORE_EVENT = {"value": 2, "unit": "minutes"}
cached_events = None


def call(event):
    global cached_events
    account_sid = TWILIO_ACCOUNT_ID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    custom_message = CUSTOM_MESSAGE.format(
        TIME_TO_CALL_BEFORE_EVENT["value"],
        TIME_TO_CALL_BEFORE_EVENT["unit"],
        event["summary"],
    )
    twiml = f'<Response><Say loop="{REPEAT_MESSAGE_VALUE}">{custom_message}</Say></Response>'

    call = client.calls.create(twiml=twiml, to=MY_NUMBER, from_=MY_TWILIO_NUMBER)
    print(call.status)
    if isinstance(cached_events, list):
        update_is_call = (
            lambda _event: event
            if (_event["id"] != event["id"])
            else {**_event, "is_call": True}
        )
        updated_events_iterator = map(update_is_call, cached_events)
        cached_events = list(updated_events_iterator)
        print(cached_events)


def get_time_difference_per_unit(time_diff_sec):
    unit = TIME_TO_CALL_BEFORE_EVENT["unit"]
    diff = {
        "seconds": time_diff_sec,
        "minutes": time_diff_sec / 60,
    }[unit]
    return diff


def get_calendar_events(user_email):
    global LAST_FETCH_TIME, cached_events
    should_fetch = True or (
        LAST_FETCH_TIME is None or time.time() - LAST_FETCH_TIME > CACHE_PERIOD
    )
    print("should_fetch: ", should_fetch)
    if should_fetch or not cached_events:
        LAST_FETCH_TIME = time.time()
        print("fetching")
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE_PATH, scopes=SCOPES
        )
        service = build("calendar", "v3", credentials=credentials)

        now = datetime.datetime.utcnow().isoformat() + "Z"

        response_events_result = (
            service.events()
            .list(
                calendarId=user_email,
                timeMin=now,
                maxResults=MAX_EVENTS_RESULTS,
                singleEvents=True,
                orderBy="startTime",
                timeZone="UTC",
            )
            .execute()
        )

        cached_events = response_events_result.get("items", [])

    events = cached_events
    if events:
        for event in events:
            event_time = event["start"]["dateTime"]
            event_timestamp = datetime.datetime.fromisoformat(
                event_time[:-1]
            ).timestamp()
            current_datetime_timestamp = datetime.datetime.utcnow().timestamp()
            time_difference_in_seconds = event_timestamp - current_datetime_timestamp
            time_difference = get_time_difference_per_unit(time_difference_in_seconds)
            print(time_difference)
            if (
                time_difference <= TIME_TO_CALL_BEFORE_EVENT["value"]
                and time_difference > 0
            ):
                call(event)
                return


if __name__ == "__main__":
    get_calendar_events(MY_EMAIL)
