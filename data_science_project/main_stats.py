    
# stats_main.py
import logging
from dotenv import load_dotenv
import os
from update_matches import MatchUpdater

# Configure logging
logging.basicConfig(
    filename='stats_update_log.log',
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

# Load environment variables for API key
#load_dotenv()
# Use the below line instead if the API key is not found and specify your .env file path
load_dotenv(dotenv_path=r"C:\Users\sebbe\Desktop\Skolsaker\data_science_project\Scripts\api_football.env")

def main():
    logging.info("Starting statistics update process...")

    api_key = os.getenv("API_KEY")
    if not api_key:
        logging.error("API key not found. Please check your .env file.")
        return

    # Initiera uppdateringsinstansen
    match_updater = MatchUpdater(api_key)

    try:
        # Uppdatera matchresultat och statistik
        match_updater.update_recent_match_results()

    except Exception as e:
        logging.error(f"An error occurred during the statistics update process: {e}")

    finally:
        match_updater.close_connection()

if __name__ == "__main__":
    main()