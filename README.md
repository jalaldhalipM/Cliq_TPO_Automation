# Google Sheets to Zoho Cliq Automation

This repository contains a Google Apps Script to automate lead collection from Google Sheets to a Zoho Cliq channel.

## Overview

Whenever a new row is added (e.g., via Google Forms) to the connected Google Sheet, this script will extract the following columns:
- `full_name`
- `phone_number`
- `email`
- `designation`
- `what_is_your_current_placement_challenge?`
- `college_/_institution_name`

It then posts a formatted message to the Zoho Cliq webhook URL.

## Setup Instructions

### 1. Add Code to Google Sheets
1. Open your Google Sheet: [Lead Sheet](https://docs.google.com/spreadsheets/d/1TSB2AG53NwGikeoetSxW8hS-WKonBi_cgIkkchBTke8/edit?usp=sharing).
2. Click on **Extensions > Apps Script** in the top menu.
3. Replace any existing code with the contents of `Code.gs` from this repository.
4. If your Cliq webhook requires a token, make sure to add it to the `CLIQ_WEBHOOK_URL` in the code.
5. Save the project (disk icon or `Ctrl + S`).

### 2. Set Up the Trigger
To make the script run automatically when new data is added:
1. In the Apps Script editor, click on the **Triggers** icon (it looks like an alarm clock) on the left sidebar.
2. Click **+ Add Trigger** in the bottom right corner.
3. Configure the trigger as follows:
   - **Choose which function to run:** `onFormSubmit`
   - **Choose which deployment should run:** `Head`
   - **Select event source:** `From spreadsheet`
   - **Select event type:** `On form submit`
4. Click **Save**.
5. Google will prompt you to authorize the script. Go through the authorization steps (you might need to click "Advanced" and "Go to project (unsafe)" since it's your own script).

### 3. Testing (Optional)
If you want to test the script with existing data:
1. Go back to your Google Sheet and refresh the page.
2. A new menu called **Lead Automation** will appear next to "Help".
3. Click **Lead Automation > Send Last Row to Cliq (Test)**.
4. It will read the last row in your sheet and send it to your Cliq channel. Check your Zoho Cliq `#tpoleads` channel to verify!
