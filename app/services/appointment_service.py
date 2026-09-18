import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = "primary"

def get_calendar_service():

    credentials = None

    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json",SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json",SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token_file:
            token_file.write(credentials.to_json())
    return build("calendar", "v3", credentials=credentials, cache_discovery=False)

def check_availability(start_time, duration_minutes=30):

    service = get_calendar_service()
    start = datetime.fromisoformat(start_time)

    if start < datetime.now(start.tzinfo):
        return False

    end = start + timedelta(minutes=duration_minutes)

    body = {
        "timeMin": start.isoformat(),
        "timeMax": end.isoformat(),
        "items": [
            {"id": CALENDAR_ID}
        ]
    }

    result = service.freebusy().query(body=body).execute()
    busy_times = result["calendars"][CALENDAR_ID]["busy"]
    return len(busy_times) == 0

def create_appointment(
    caller_name,
    start_time,
    duration_minutes=30
):
    if not check_availability(start_time, duration_minutes):
        return None

    service = get_calendar_service()

    start = datetime.fromisoformat(start_time)
    end = start + timedelta(minutes=duration_minutes)

    event = {
        "summary": f"Appointment - {caller_name}",
        "description": "Booked through Vapi voice appointment agent",
        "start": {
            "dateTime": start.isoformat()
        },
        "end": {
            "dateTime": end.isoformat()
        }
    }

    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event
    ).execute()

    return {
        "appointment_id": created_event["id"],
        "start_time": created_event["start"]["dateTime"]
    }

def find_appointment(appointment_id):

    service = get_calendar_service()
    try:
        event = service.events().get(calendarId=CALENDAR_ID,eventId=appointment_id).execute()
        return event
    except HttpError as error:
        if error.resp.status == 404:
            return None
        raise

def reschedule_appointment(appointment_id,new_start_time,duration_minutes=30):

    event = find_appointment(appointment_id)
    if event is None:
        return None

    if not check_availability(new_start_time, duration_minutes):
        return None

    service = get_calendar_service()
    new_start = datetime.fromisoformat(new_start_time)
    new_end = new_start + timedelta(minutes=duration_minutes)
    old_start = event["start"]["dateTime"]
    event["start"]["dateTime"] = new_start.isoformat()
    event["end"]["dateTime"] = new_end.isoformat()
    updated_event = service.events().update(calendarId=CALENDAR_ID,eventId=appointment_id,body=event).execute()

    return {
        "appointment_id": updated_event["id"],
        "old_start_time": old_start,
        "new_start_time": updated_event["start"]["dateTime"]
    }

def cancel_appointment(appointment_id):
    service = get_calendar_service()
    try:
        service.events().delete(calendarId=CALENDAR_ID,eventId=appointment_id).execute()
        return True
    except HttpError as error:
        if error.resp.status == 404:
            return False
        raise