import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    credentials = None

    if os.path.exists("../token.json"):
        credentials = Credentials.from_authorized_user_file(
            "../token.json",
            SCOPES
        )

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "../credentials.json",
                SCOPES
            )
            credentials = flow.run_local_server(port=0)

        with open("../token.json", "w") as token_file:
            token_file.write(credentials.to_json())

    return build("calendar", "v3", credentials=credentials)


def main():
    service = get_calendar_service()

    calendar = service.calendars().get(
        calendarId="primary"
    ).execute()

    print("Connected successfully.")
    print("Calendar:", calendar["summary"])


if __name__ == "__main__":
    main()