# my-reminder

# Google Calendar Meeting Notifier

## Description

Google Calendar Meeting Notifier is a Python script that fetches upcoming events from your Google Calendar and automatically calls your specified phone number as a timely reminder for your scheduled meetings.

## Key Features

- Utilizes the Google Calendar API to access and retrieve upcoming events.
- Periodic execution ensures real-time calls for scheduled meetings.
- Configurable time threshold to determine when to trigger the phone call notification.
- Customizable phone number, allowing users to define their preferred contact number.
- Requires a Twilio account and Twilio API keys for making phone calls.
- Supports dynamic voice synthesis, providing flexibility to choose different voice styles.(explore Twilio developers doc)

## Requirements

- Python 3.x
- Google Calendar API service account credentials (JSON key file)
- Twilio account with Twilio API keys (Account SID and Auth Token)
- Twilio Python library (for making phone calls)

## Installation

1. Clone this repository to your local machine:
2. Install the required Python packages:
3. Obtain Google Calendar API service account credentials:

- Go to the Google Cloud Console: https://console.cloud.google.com/
- Create a new project and enable the Google Calendar API.
- Create service account credentials and download the JSON key file.
- Save the JSON key file in the project directory as `credentials.json`.

4. Set up a Twilio account and obtain your Twilio API keys:

- Sign up for a Twilio account: https://www.twilio.com/try-twilio
- Obtain your Account SID and Auth Token from the Twilio dashboard.
- Provide your Twilio API keys in the script.

## Usage

1. Run the script to check for upcoming meetings and receive timely notifications:
2. For automatic periodic execution, set up a task scheduler or cron job to run the script at desired intervals. you can use long-period services

## Note

- This project is intended to provide a convenient way to receive timely notifications for scheduled Google Calendar events, empowering users to manage their time efficiently and stay on top of their appointments.
- To use the phone call functionality, users are required to set up a Twilio account and provide their Twilio API keys (Account SID and Auth Token) in the script.
- Please ensure you follow the API usage policies and terms of service for both Google Calendar and Twilio when using this script.

## License

This project is licensed under the [MIT License](LICENSE).
