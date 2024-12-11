Telegram Bot for Alert Notifications
This bot provides notifications about various emergencies in Ukraine, including air raids and artillery shelling, using Telegram. It uses the alerts.in.ua API to fetch real-time data about alerts and sends them to users based on their preferences.

Features
Receive notifications about active alerts in Ukraine.
Toggle notifications on or off.
Choose between receiving alerts for the entire country or by specific regions.
View screenshots of alerts from the alerts.in.ua website.
Libraries and Frameworks Used
python-telegram-bot: The main library to interact with Telegram's Bot API.
selenium: Used to capture screenshots from the alerts.in.ua website.
requests: Used for making HTTP requests.
alerts_in_ua: A custom library for interacting with the alerts.in.ua API.
datetime: For handling time-related operations.
threading: Used to run background tasks like checking alerts.

Usage
Interact with the bot:
/start: Initializes the bot and sends a greeting.
/settings: Shows options for region or country-based alerts, and toggles notifications.
/map: Sends a screenshot of the alerts.in.ua website.
Choose a region: You can select specific regions to receive alerts.