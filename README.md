# Lead Automation: Google Sheets to Zoho Cliq

This repository contains robust automation tools to sync lead data from a Google Sheet to a Zoho Cliq channel (`#tpoleads`). 

We provide two flexible solutions to fit your infrastructure:
1. **Python Automation (Recommended):** A professional, dependency-free Python script designed for local machines, VPS, or cloud environments. It tracks state locally to prevent duplicate notifications.
2. **Google Apps Script:** A serverless solution that triggers instantly on form submission inside Google Sheets.

---

## 🚀 Option A: Zero-Dependency Python Automation (Recommended)

The Python automation is designed to be highly reliable, fast, and secure. It runs on **any machine with Python 3 installed** without needing any `pip install` packages!

### Features
- **Zero External Dependencies:** Uses Python's standard library (`urllib`, `csv`, `json`). No `pip install` required!
- **Duplicate Prevention:** Tracks processed leads in a local `processed_leads.txt` state file to prevent duplicate alerts.
- **Dry-run Mode:** Test the formatting and parser without posting to Zoho Cliq.
- **Daemon Loop Mode:** Can run as a continuous background process polling for updates.
- **Secure Configuration:** Loads sensitive tokens and URLs from a `.env` file (which is ignored by Git and never committed to GitHub).

### Setup and Configuration

1. **Verify Python is installed:**
   ```powershell
   py --version
   # or
   python3 --version
   ```

2. **Configure Environment Variables:**
   - Copy `.env.template` to `.env`.
   - Update the values inside the `.env` file with your Google Sheet CSV export link and Zoho Cliq Webhook URL:
     ```ini
     GOOGLE_SHEET_CSV_URL="https://docs.google.com/spreadsheets/d/1TSB2AG53NwGikeoetSxW8hS-WKonBi_cgIkkchBTke8/export?format=csv"
     CLIQ_WEBHOOK_URL="https://cliq.zoho.com/company/902162992/api/v2/channelsbyname/tpoleads/message"
     POLL_INTERVAL=60
     ```

3. **Running the Automation:**
   * **Dry-Run (Test configuration and printing payloads without sending):**
     ```powershell
     py automation.py --dry-run --send-all
     ```
   * **Single Execution (Checks once and exits; perfect for Windows Task Scheduler or Linux Cron):**
     ```powershell
     py automation.py
     ```
   * **Daemon Mode (Runs continuously in the background, checking for new rows every X seconds):**
     ```powershell
     py automation.py --loop --interval 60
     ```

### Production Deployment & Scheduling
* **On Windows (Task Scheduler):**
  Create a basic task in Windows Task Scheduler to run `py C:\path\to\automation.py` every 5-10 minutes.
* **On Linux (Cron):**
  Add a cron job using `crontab -e`:
  ```bash
  */5 * * * * cd /path/to/Cliq_TPO_Automation && python3 automation.py >> automation.log 2>&1
  ```

---

## ⚡ Option B: Google Apps Script Trigger

If you prefer a pure cloud, event-driven execution that fires the exact instant a Google Form is submitted:

### Setup Instructions
1. Open your [Google Sheet](https://docs.google.com/spreadsheets/d/1TSB2AG53NwGikeoetSxW8hS-WKonBi_cgIkkchBTke8/edit?usp=sharing).
2. Click **Extensions > Apps Script**.
3. Replace the existing script with the contents of [Code.gs](file:///c:/Users/Admin/Desktop/Cliq_TPO_Automation/Code.gs).
4. Save the project and configure a trigger:
   - Click the **Triggers** icon (alarm clock) on the left sidebar.
   - Click **+ Add Trigger** in the bottom right.
   - Set **Which function to run** to `onFormSubmit`.
   - Set **Deployment** to `Head`.
   - Set **Event source** to `From spreadsheet`.
   - Set **Event type** to `On form submit` and click **Save**.
