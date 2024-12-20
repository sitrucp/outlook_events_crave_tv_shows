# Crave TV Data Outlook Event Creation

This repository contains scripts to process Crave TV viewing history data and create Outlook calendar events using the Microsoft Graph API.

Crave TV doesn't provide a data export feature. They do provide a web page with past 90 days watch history. You could scrape the web html table however a more complete set of watch history data is available as json objects in the Dev Tools console network tab.

## Features
1. **Data Cleaning**: Preprocess Crave TV viewing history data.
2. **Event Creation**: Create Outlook calendar events for viewing entries.

## Workflow Summary
1. Get Crave TV watch history data from web page https://www.crave.ca/en/cravings?tab=watch-history.
2. Run `process_raw_data.py` which will get all json files and merge and refine their data and save it as raw_data_clean.csv
3. Run `create_events.py` to create Outlook events from the cleaned raw_data_clean.csv file.

## Prerequisites
- **Microsoft Graph API Credentials**: `client_id`, `tenant_id`, `client_secret`, `user_id`
- **Required Libraries**:  `pandas`, `numpy`, `requests`, `pytz`

## Usage

### Step 1: Obtain Your Crave TV Viewing History
1. Go  Crave TV watch history page https://www.crave.ca/en/cravings?tab=watch-history.
2. Open Dev Tools to view console network tab. Look for the following objects:

   - watchHistory?pageNumber=0&pageSize=500 - note there might be more than one of these objects
   - graphql_0.json - note there might be more than one of these objects

3. Copy the json from both of these objects and save files with their original object names:
   - watchHistory_pageNumber_0.json
   - graphql_0.json

### Step 2: Clean the Data
Run the `process_raw_data.py` script which will get all json files and merge and refine their data and save it as raw_data_clean.csv

### Step 3: Create Outlook Calendar Events
Run the `create_events.py` script to create calendar events using the cleaned data `raw_data_clean.csv` (generated in Step 2)

## Example Directory Structure
```
repo/
|
├── process_raw_data.py
├── create_events.py
├── watchHistory_pageNumber_0.json
├── graphql_0.json
├── raw_data_clean.csv
├── create_events_log.txt
├── last_event_log.csv
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

