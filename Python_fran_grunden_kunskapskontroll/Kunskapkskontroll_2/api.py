import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path='C:/Users/sebbe/Desktop/Skolsaker/Python_f_grunden/Kunskapskontroll2/api_key.env')

class API:
    """A class to fetch data from odds API."""
    def __init__(self):
        

        self.api_key = os.getenv("API_KEY")
        self.api_url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
        self.logger = logging.getLogger(__name__)

    def fetch_data(self):
        self.logger.info('Fetching data...')
        params = {
            "apiKey": self.api_key,
            "regions": "eu",  # eu odds
            "markets": "h2h",  # h2h odds
            "oddsFormat": "decimal",  # odds in decimal
            "dateFormat": "iso"  # time format
        }
        
        response = requests.get(self.api_url, params = params)
        self.logger.info(f"Response code: {response.status_code}")
        
        if response.status_code == 200: # 200 because that means ok 
            self.logger.info("Data fetched successfully")
            return response.json()
    
        else:
            self.logger.error(f"Could not fetch data with error code:{response.status_code}.")
            self.logger.error(f"Error response: {response.text}")
            return None
