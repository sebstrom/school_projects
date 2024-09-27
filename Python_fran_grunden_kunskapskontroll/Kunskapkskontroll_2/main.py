import os
import logging
from api import API
from datacleaner import DataCleaner
from datasaver import DataSaver
from dotenv import load_dotenv


# create logger 
logging.basicConfig(
    filename='pipeline.log', 
    format='[%(asctime)s][%(name)s] %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S', 
    level=logging.DEBUG)

# load our api key 
load_dotenv(dotenv_path='C:/Users/sebbe/Desktop/Skolsaker/Python_f_grunden/Kunskapskontroll2/api_key.env')



def main():
    """Main function to retrieve, clean, save and log data"""
    api_key = os.getenv("API_KEY")

    api = API()
    odds_data = api.fetch_data()
    
    if not odds_data:
        logging.error("Unable to retrieve data")
        return
    
    cleaner = DataCleaner()
    clean_data = cleaner.clean_data(odds_data)
    
    saver = DataSaver()
    saver.save_data(clean_data)
    
    logging.info("Able to retrieve and save data")

if __name__ == "__main__":
    main()