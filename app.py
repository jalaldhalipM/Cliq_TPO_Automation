import os
import threading
import time
import logging
from flask import Flask, jsonify
import automation

# Configure Flask app
app = Flask(__name__)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Load local environment variables (if any) for local testing
automation.load_env()

@app.route('/')
def home():
    """
    Health check endpoint to satisfy Render's HTTP service port check.
    """
    return jsonify({
        "status": "running",
        "service": "Google Sheets to Zoho Cliq Lead Automation",
        "timestamp": time.time()
    })

@app.route('/sync')
def manual_sync():
    """
    HTTP endpoint to trigger an on-demand manual lead check.
    Allows triggering a sync by hitting https://<your-render-url>/sync
    """
    sheet_url = os.environ.get("GOOGLE_SHEET_CSV_URL")
    webhook_url = os.environ.get("CLIQ_WEBHOOK_URL")

    if not sheet_url or not webhook_url:
        return jsonify({
            "status": "error",
            "message": "Required environment variables GOOGLE_SHEET_CSV_URL or CLIQ_WEBHOOK_URL are missing."
        }), 500

    try:
        # Trigger lead check
        logging.info("Manual sync triggered via HTTP endpoint...")
        automation.check_for_new_leads(sheet_url, webhook_url, dry_run=False, send_all=False)
        return jsonify({
            "status": "success",
            "message": "Lead sync triggered successfully. Check console logs for details."
        })
    except Exception as e:
        logging.error(f"Error during manual lead sync: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def background_poll_loop():
    """
    Runs the polling check periodically in a background thread.
    """
    sheet_url = os.environ.get("GOOGLE_SHEET_CSV_URL")
    webhook_url = os.environ.get("CLIQ_WEBHOOK_URL")
    poll_interval = int(os.environ.get("POLL_INTERVAL", 60))

    if not sheet_url or not webhook_url:
        logging.critical("Background thread failed: GOOGLE_SHEET_CSV_URL or CLIQ_WEBHOOK_URL is not set.")
        return

    logging.info(f"Starting background automation loop (polling every {poll_interval}s)...")
    while True:
        try:
            automation.check_for_new_leads(sheet_url, webhook_url, dry_run=False, send_all=False)
        except Exception as e:
            logging.error(f"Error in background polling thread: {e}")
        
        time.sleep(poll_interval)

# Start the continuous background polling thread
poll_thread = threading.Thread(target=background_poll_loop, daemon=True)
poll_thread.start()

if __name__ == '__main__':
    # Bind to Render's dynamic PORT environment variable (default: 10000)
    port = int(os.environ.get("PORT", 10000))
    # Run the server
    app.run(host='0.0.0.0', port=port)
