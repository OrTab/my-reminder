import datetime
import time
from multiprocessing import Process, Manager
from google.oauth2 import service_account
from googleapiclient.discovery import build
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
    FETCH_PERIOD,
    SLEEP_PERIOD,
    WEB_HOOK_URL,
    CREDENTIALS_FILE_PATH,
)
from twilio.rest import Client
from server.server import init_server
from cached_events_util import update_event_property

LAST_FETCH_TIME = None
TIME_TO_CALL_BEFORE_EVENT = {"value": 1, "unit": "minutes"}
cached_events = None


def call(event):
    global cached_event
    account_sid = TWILIO_ACCOUNT_ID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    custom_message = CUSTOM_MESSAGE.format(
        TIME_TO_CALL_BEFORE_EVENT["value"],
        TIME_TO_CALL_BEFORE_EVENT["unit"],
        event["summary"],
    )
    twiml = f'<Response><Say loop="{REPEAT_MESSAGE_VALUE}">{custom_message}</Say></Response>'

    call = client.calls.create(
        twiml=twiml,
        to=MY_NUMBER,
        from_=MY_TWILIO_NUMBER,
        status_callback=WEB_HOOK_URL,
        status_callback_event=["initiated", "ringing", "answered", "completed"],
    )
    update_event_property(cached_events, "id", event["id"], "call_id", call.sid)


def get_time_difference_per_unit(time_diff_sec):
    unit = TIME_TO_CALL_BEFORE_EVENT["unit"]
    diff = {
        "seconds": time_diff_sec,
        "minutes": time_diff_sec / 60,
    }[unit]
    return diff


def get_calendar_events(user_email):
    global LAST_FETCH_TIME, cached_events
    should_fetch = (
        LAST_FETCH_TIME is None or time.time() - LAST_FETCH_TIME > FETCH_PERIOD
    ) or not cached_events["data"]
    print("Should fetch: ", should_fetch)
    if should_fetch:
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

        cached_events["data"] = response_events_result.get("items", [])

    events = cached_events["data"]
    if events:
        for event in events:
            event_time_start = event["start"]
            if "dateTime" not in event_time_start:
                continue
            event_time = event["start"]["dateTime"]
            event_timestamp = datetime.datetime.fromisoformat(
                event_time[:-1]
            ).timestamp()
            current_datetime_timestamp = datetime.datetime.utcnow().timestamp()
            time_difference_in_seconds = event_timestamp - current_datetime_timestamp
            time_difference = get_time_difference_per_unit(time_difference_in_seconds)
            if (
                time_difference <= TIME_TO_CALL_BEFORE_EVENT["value"]
                and time_difference > 0
            ):
                call(event)
                return
        print(
            "No meeting in the next {} {}".format(
                TIME_TO_CALL_BEFORE_EVENT["value"], TIME_TO_CALL_BEFORE_EVENT["unit"]
            )
        )


if __name__ == "__main__":
    manager = Manager()
    cached_events = manager.dict()
    server_process = Process(target=init_server, args=(cached_events,))
    server_process.start()
    while True:
        get_calendar_events(MY_EMAIL)
        time.sleep(SLEEP_PERIOD)
