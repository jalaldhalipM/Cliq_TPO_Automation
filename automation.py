#!/usr/bin/env python3
"""
Google Sheets to Zoho Cliq Lead Automation
------------------------------------------
Author: Antigravity AI Pair Programmer
Description: Periodically checks a Google Sheet for new leads and sends
             selected lead information to a Zoho Cliq channel webhook.
Requirements: Python 3+ (Standard Library Only - No Pip Install Required)
"""

import os
import sys
import csv
import json
import time
import io
import urllib.request
import logging
import argparse
import hashlib

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

STATE_FILE = "processed_leads.txt"

def load_env(env_path=".env"):
    """
    Parses a local .env file and updates os.environ.
    This eliminates the need for the external `python-dotenv` library.
    """
    if not os.path.exists(env_path):
        logging.warning(f"No configuration file found at {env_path}. Relying on system environment variables.")
        return

    logging.info(f"Loading configuration from {env_path}...")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignore empty lines and comments
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # Strip optional surrounding quotes
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                os.environ[key] = val

def load_processed_ids(state_file_path=STATE_FILE):
    """
    Loads already processed lead IDs from the local state file.
    """
    if not os.path.exists(state_file_path):
        return set()
    
    with open(state_file_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def save_processed_id(lead_id, state_file_path=STATE_FILE):
    """
    Appends a successfully processed lead ID to the local state file.
    """
    with open(state_file_path, "a", encoding="utf-8") as f:
        f.write(f"{lead_id}\n")

def get_row_id(row):
    """
    Returns a unique identifier for the row.
    Falls back to a SHA256 hash of core columns if 'id' is blank or missing.
    """
    row_id = row.get("id")
    if row_id and row_id.strip():
        return row_id.strip()
    
    # Hash details for rows without a explicit unique id
    components = [
        row.get("created_time", ""),
        row.get("email", ""),
        row.get("phone_number", ""),
        row.get("full_name", "")
    ]
    hash_input = "|".join(components).encode("utf-8")
    return hashlib.sha256(hash_input).hexdigest()

def fetch_sheet_data(url):
    """
    Fetches the public Google Sheet export in CSV format and returns a list of dictionaries.
    """
    logging.info("Fetching spreadsheet data...")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LeadAutomation/1.0"}
    )
    
    with urllib.request.urlopen(req) as response:
        content = response.read().decode("utf-8")
    
    f = io.StringIO(content)
    reader = csv.DictReader(f)
    
    # Clean keys and return list
    data = []
    for row in reader:
        cleaned_row = {k.strip() if k else "": v.strip() if v else "" for k, v in row.items()}
        data.append(cleaned_row)
    
    return data

def format_lead_message(row):
    """
    Formats the Zoho Cliq markdown message payload using the requested columns.
    """
    full_name = row.get("full_name") or "N/A"
    phone_number = row.get("phone_number") or "N/A"
    email = row.get("email") or "N/A"
    designation = row.get("designation") or "N/A"
    challenge = row.get("what_is_your_current_placement_challenge?") or "N/A"
    college = row.get("college_/_institution_name") or "N/A"
    
    # Clean up double underscores or formatting if needed
    message = (
        "🚀 *New Lead Received*\n\n"
        f"*Name:* {full_name}\n"
        f"*Phone:* {phone_number}\n"
        f"*Email:* {email}\n"
        f"*Designation:* {designation}\n"
        f"*College/Institution:* {college}\n"
        f"*Challenge:* {challenge}"
    )
    return message

def send_to_cliq(webhook_url, message_text, dry_run=False):
    """
    Sends a POST request with the formatted message to Zoho Cliq.
    """
    payload = {
        "text": message_text,
        "bot": {
            "name": "Lead Automation Bot",
            "image": "https://cdn-icons-png.flaticon.com/512/4144/4144673.png"
        }
    }
    
    if dry_run:
        logging.info(f"[DRY-RUN] Would send payload to Cliq:\n{json.dumps(payload, indent=2)}")
        return True

    logging.info("Sending message to Zoho Cliq...")
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LeadAutomation/1.0"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_content = response.read().decode("utf-8")
            logging.info(f"Zoho Cliq response: {res_content}")
            return True
    except Exception as e:
        logging.error(f"Error posting to Zoho Cliq channel: {e}")
        return False

def check_for_new_leads(sheet_url, webhook_url, dry_run=False, send_all=False):
    """
    Fetches the Google Sheet, compares against processed leads, and triggers notifications.
    """
    try:
        rows = fetch_sheet_data(sheet_url)
    except Exception as e:
        logging.error(f"Error fetching Google Sheet: {e}")
        return

    total_rows = len(rows)
    logging.info(f"Loaded {total_rows} rows from the spreadsheet.")

    if total_rows == 0:
        logging.info("The spreadsheet is empty.")
        return

    # Check if the state file exists to determine if this is the initial run
    state_exists = os.path.exists(STATE_FILE)
    processed_ids = load_processed_ids()
    
    new_leads = []
    
    for row in rows:
        row_id = get_row_id(row)
        if row_id not in processed_ids:
            new_leads.append((row_id, row))
            
    if not new_leads:
        logging.info("No new leads found.")
        return

    logging.info(f"Found {len(new_leads)} leads not in the local state.")

    # Guard against spamming existing rows on the first run
    if not state_exists and not send_all:
        logging.warning("=== First-Time Run Notice ===")
        logging.warning("No state file 'processed_leads.txt' was found.")
        logging.warning("To prevent spamming your Zoho Cliq channel, all existing rows will be marked as processed.")
        logging.warning("If you want to send all existing leads to Cliq, run this script with the --send-all flag.")
        logging.warning("=============================")
        
        # Populate the state file with all current lead IDs without sending
        if not dry_run:
            for row_id, _ in new_leads:
                save_processed_id(row_id)
            logging.info(f"Successfully marked {len(new_leads)} existing leads as processed.")
        else:
            logging.info(f"[DRY-RUN] Would mark {len(new_leads)} existing leads as processed.")
        return

    # Send notifications starting from the oldest (top of sheet) to the newest (bottom of sheet)
    success_count = 0
    for row_id, row in new_leads:
        message = format_lead_message(row)
        
        if send_to_cliq(webhook_url, message, dry_run):
            if not dry_run:
                save_processed_id(row_id)
            success_count += 1
            # Add a small delay between posts to prevent API rate limiting
            time.sleep(1)
            
    logging.info(f"Process complete: Successfully processed {success_count}/{len(new_leads)} new leads.")

def main():
    parser = argparse.ArgumentParser(description="Google Sheets to Zoho Cliq Lead Automation Daemon.")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Print payloads to console without sending them to Zoho Cliq.")
    parser.add_argument("-l", "--loop", action="store_true", help="Run continuously in a polling loop instead of a single execution.")
    parser.add_argument("--send-all", action="store_true", help="On first run, send all existing sheet leads instead of marking them processed.")
    parser.add_argument("-i", "--interval", type=int, help="Polling interval in seconds (overrides POLL_INTERVAL in .env file).")
    
    args = parser.parse_args()

    # Load configuration
    load_env()
    
    sheet_url = os.environ.get("GOOGLE_SHEET_CSV_URL")
    webhook_url = os.environ.get("CLIQ_WEBHOOK_URL")
    
    if not sheet_url:
        logging.critical("GOOGLE_SHEET_CSV_URL is not set in environment variables or .env file.")
        sys.exit(1)
        
    if not webhook_url:
        logging.critical("CLIQ_WEBHOOK_URL is not set in environment variables or .env file.")
        sys.exit(1)

    poll_interval = args.interval or int(os.environ.get("POLL_INTERVAL", 60))

    if args.dry_run:
        logging.info("Starting in DRY-RUN mode. No webhooks will be triggered.")

    if args.loop:
        logging.info(f"Starting lead automation daemon (polling interval: {poll_interval}s)...")
        try:
            while True:
                check_for_new_leads(sheet_url, webhook_url, args.dry_run, args.send_all)
                logging.info(f"Sleeping for {poll_interval} seconds...")
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            logging.info("Lead automation daemon stopped gracefully by user.")
    else:
        logging.info("Starting single-run lead check...")
        check_for_new_leads(sheet_url, webhook_url, args.dry_run, args.send_all)

if __name__ == "__main__":
    main()
