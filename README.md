## Overview
This update introduces several new features and improvements to the bot. These include the addition of map screenshot sharing, region-based alert monitoring, and logging. Additionally, a new function monitor_alerts_status has been started to track alert completion times for specific regions. Minor bug fixes and enhancements have also been implemented.

## New Features
## 1. Map Screenshot Sending
A new feature to send a screenshot of the alerts map has been implemented.
Requirements: To use this feature, the following dependencies must be installed:
Google Chrome
A compatible web driver (e.g., chromedriver) should be installed and configured on the system.
The send_screenshot function captures the screenshot and sends it as a photo through the bot.
## 2. Region-Based Alert Monitoring
Users can now select a region and get alerts specifically for that area.
Active alerts for each region can be viewed upon request.
Users can choose their region by clicking on buttons in the Telegram interface, and the bot will filter alerts based on the selected region.
## 3. monitor_alerts_status Function (WIP)
A new feature is under development to monitor the status of active alerts and calculate their completion time for specific regions.
When an alert is finished, the bot will send a message indicating the start time, end time, and duration of the alert for the selected region.
## 4. Logging
A logging system has been added to track errors and provide feedback on the bot’s activities.
Logs are stored with timestamps, error levels, and details for troubleshooting.
## 5. User Dictionaries
Several dictionaries have been added to track user states, regions, and notifications:
region_select_users: Stores users who have selected a region.
notifications_on_users / notifications_off_users: Track users who have turned on or off notifications.
active_alerts_dict: Stores currently active alerts.
## 6. Minor Bug Fixes
Fixed minor issues related to state management and user interactions.