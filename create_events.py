import pandas as pd
import time
import requests
import sys 
import os
import logging


#--- Get msgraph config variables ---#
config_msgraph_path = os.getenv("ENV_VARS_PATH")  # Get path to directory contaiining config_msgraph.py
if not config_msgraph_path:
    raise ValueError("ENV_VARS_PATH environment variable not set")
sys.path.insert(0, config_msgraph_path)

from config_msgraph import config_msgraph

client_id=config_msgraph["client_id"]
tenant_id=config_msgraph["tenant_id"]
client_secret=config_msgraph["client_secret"]
user_id=config_msgraph["user_id"]

#--- Data source ---#
input_file = "raw_data_clean.csv"
last_event_log = "last_event_log.csv"
create_events_log = "create_events_log.txt"

#--- Setup logging ---#
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(create_events_log),
        logging.StreamHandler(sys.stdout)
    ]
)

#--- Function to obtain an access token ---#
def get_access_token(client_id, tenant_id, client_secret):
    logging.info("Obtaining access token from Microsoft Graph API")
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # Raises an exception for HTTP error codes
    logging.info("Access token obtained successfully")
    return response.json().get('access_token')

#--- Function to create a calendar event using Microsoft Graph API ---#
def create_calendar_event(access_token, row):
    logging.info("Starting to create a calendar event")
    # Format the start and end times for the event payload
    start_time_formatted = row['start_datetime_EST'].strftime('%Y-%m-%dT%H:%M:%S')
    end_time_formatted = row['end_datetime_EST'].strftime('%Y-%m-%dT%H:%M:%S')

    # Determine title_complete based on mediaType
    if row['media_type'] == 'movie':
        title_complete = row['show_name']
    elif row['media_type'] == 'series':
        title_complete = f"{row['show_name'] } - {row['episode_name']} S{row['season']} E{row['episode']}"
    else:
        title_complete = row['show_name']

    # create the event description
    description_html = (
        f"Title: {title_complete}<br>"
        f"Start: {start_time_formatted}<br>"
        f"End: {end_time_formatted}<br>"
        f"Duration: {row['duration_hh_mm_ss']}<br>"
        f"Attributes: {(str(row['media_type']).lower().replace(',', ', ') if pd.notna(row['media_type']) else 'None')}"
    )

    # Then, include this HTML-formatted description in your payload
    event_payload = {
        "subject": f"Crave TV: {title_complete}",
        "start": {
            "dateTime": start_time_formatted,
            "timeZone": "America/Toronto"
        },
        "end": {
            "dateTime": end_time_formatted,
            "timeZone": "America/Toronto"
        },
        "body": {
            "contentType": "HTML",
            "content": description_html
        },
        "categories": ["Crave TV"]
    }

    # Send the request to create the event
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    response = requests.post(f"https://graph.microsoft.com/v1.0/users/{user_id}/events",
                             headers=headers, json=event_payload)
    response.raise_for_status()  # Ensure successful request

#--- Main script to process the CSV data and create events ---#
def main():
    # Obtain access token
    access_token = get_access_token(client_id, tenant_id, client_secret)

   # Read the CSV file, ensuring datetime parsing
    # Read the CSV file, ensuring datetime parsing
    df = pd.read_csv(input_file, parse_dates=["start_datetime_EST", "end_datetime_EST"]) 

    # Iterate over rows and create calendar events
    for index, row in df.iterrows():
        try:
            create_calendar_event(access_token, row)
            print(f"Event created for {row['start_datetime_EST']}-{row['show_name']}-{row['episode_name']}-S{row['season']} E{row['episode']}")
            #break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Extract wait time from 'Retry-After' or default to 60 seconds
                retry_after = int(e.response.headers.get('Retry-After', 60))
                print(f"Rate limit hit, waiting for {retry_after} seconds before retrying...")
                time.sleep(retry_after)  
                # Optionally, retry the failed request here or log it for a manual retry later
            else:
                print(f"Failed to create event for {row['start_datetime_EST']}-{row['show_name']}-{row['episode_name']}-S{row['season']} E{row['episode']}. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while creating the event for {row['start_datetime_EST']}-{row['show_name']}-{row['episode_name']}-S{row['season']} E{row['episode']}. Error: {e}")

if __name__ == "__main__":
    main()

