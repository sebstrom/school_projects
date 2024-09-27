import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='C:/Users/sebbe/Desktop/Skolsaker/Python_f_grunden/Kunskapskontroll2/api_key.env')

# API key test 
def test_load_api_key():
    """test to check if my api key loads correctly"""
    api_key = os.getenv("API_KEY")
    assert api_key is not None, "API key is not loaded from the .env file"
    
# Api request test     
def test_api():
    """Test that api works"""
    
    api_key = os.getenv("API_KEY")
    params = {
        "apiKey": api_key,
        "regions": "eu",  # eu odds
        "markets": "h2h",  # h2h odds
        "oddsFormat": "decimal",  # odds i decimal
        "dateFormat": "iso"  # tidsformat
    }
    
    url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
    response = requests.get(url, params=params)
    
    print(f"Response status code: {response.status_code}")
    print(f"Response body: {response.text}")
    
    assert response.status_code == 200