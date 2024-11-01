# main_odds.py

import logging
from save_odds import OddsSaver
from dotenv import load_dotenv
import os


logging.basicConfig(
    filename='odds_log.log', 
    format='[%(asctime)s][%(levelname)s] %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S', 
    level=logging.DEBUG
)

# Load environment variables

load_dotenv()
# Use the below line instead if the API key is not found and specify your .env file path
#load_dotenv(dotenv_path="your filepath here")


def main():
    logging.info("Starting odds fetching process...")
    
    api_key = os.getenv("API_KEY")
    logging.info(f"API Key: {api_key}")
    if not api_key:
        logging.error("API key not found.")
        return
    
    odds_saver = OddsSaver(api_key)
    
    try:
        odds_saver.process_leagues()
        logging.info("Odds fetching completed successfully.")
    except Exception as e:
        logging.error(f"Error occurred while fetching odds: {e}")
    finally:
        odds_saver.close_connection()

if __name__ == "__main__":
    main()
