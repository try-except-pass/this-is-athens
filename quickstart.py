import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from datetime import datetime
from ThisIsAthens import *

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")

  return service

if __name__ == "__main__":
  service = main()

list_of_events = get_events()
for x in list_of_events:
  id = clean2(x.name() + "thisisathenss")
  try:
    event = service.events().get(calendarId='primary', eventId=id).execute()
  except:
    if x.duration():
      event = {
        'id': id,
        'summary': x.name(),
        'location': x.location(),
        'description': x.description() + '\n' + x.time() + '\n' + x.tickets() + '\n' + x.social(),
        'start': {
          'date': x.date()[0]
        },
        'end': {
          'date': x.date()[-1]
        },
        'transparency': 'transparent',
        'reminders': {
          'useDefault': False
        }
      }
      event_result = service.events().insert(calendarId='primary', body=event).execute()
      print('Event created: %s' % (event_result.get('htmlLink')))
    else:
      pass