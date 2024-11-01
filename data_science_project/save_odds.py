import requests
import logging
from datetime import datetime, timedelta
from db_connector import get_db_connection, close_db_connection

class OddsSaver:
    def __init__(self, api_key):
        self.api_key = api_key
        self.allowed_bookmakers = ["Unibet"]
        self.conn, self.cursor = get_db_connection()
        logging.basicConfig(level=logging.DEBUG, filename='odds_log.log',
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def fetch_upcoming_matches(self, league_key):
        """Fetch upcoming matches directly from the Odds API."""
        today = datetime.today()
        ten_days_after = today + timedelta(days=10)
        today_str = today.strftime('%Y-%m-%d')
        ten_days_after_str = ten_days_after.strftime('%Y-%m-%d')

        logging.info(f"Fetching odds for upcoming matches between {today_str} and {ten_days_after_str}")

        url = f"https://api.the-odds-api.com/v4/sports/{league_key}/odds/"
        params = {
            'apiKey': self.api_key,
            'regions': 'eu',
            'markets': 'h2h',
            'oddsFormat': 'decimal',
            'dateFormat': 'iso',
            'from': today_str,
            'to': ten_days_after_str
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            logging.info(f"Matches fetched successfully for {league_key}")
            return response.json()
        else:
            logging.error(f"Error fetching matches: {response.status_code} - {response.text}")
            return None

    def save_odds_to_db(self, odds_data, league_key, leagues):
        logging.info(f"Saving odds to database for league_key: {league_key}")
        
        insert_query = """
        INSERT INTO odds_new (match_id, bookmaker, home_odds, draw_odds, away_odds, league_id, season, event_date, home_team_name, away_team_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            home_odds=VALUES(home_odds), 
            draw_odds=VALUES(draw_odds), 
            away_odds=VALUES(away_odds),
            home_team_name=VALUES(home_team_name),
            away_team_name=VALUES(away_team_name),
            league_id=VALUES(league_id), 
            season=VALUES(season), 
            event_date=VALUES(event_date)
        """
        
        for match in odds_data:  # Iterate through the list of matches
            try:
                for bookmaker_data in match['bookmakers']:
                    if bookmaker_data['title'].lower() == 'unibet':
                        match_id = match['id']
                        home_team = match['home_team']
                        away_team = match['away_team']
                        h2h_odds = bookmaker_data['markets'][0]['outcomes']
                        home_odds = h2h_odds[0]['price']
                        draw_odds = h2h_odds[1]['price']
                        away_odds = h2h_odds[2]['price']
                        league_id = leagues[league_key]
                        season = 2024
                        event_date = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ").date()
                        
                        logging.info(f"Saving match with ID: {match_id}, Teams: {home_team} vs {away_team}, Odds: {home_odds}, {draw_odds}, {away_odds}, Date: {event_date}")


                        # Insert into the database without team IDs
                        self.cursor.execute(insert_query, (match_id, "Unibet", home_odds, draw_odds, away_odds, league_id, season, event_date, home_team, away_team))
                        self.conn.commit()
                        logging.info(f"Odds successfully saved for match {match_id}")
                        
            except Exception as e:
                logging.error(f"Error saving odds for match {match_id}: {e}")



    def process_leagues(self):
        """Main function to run fetching and saving process for all leagues."""
        leagues = {
            'soccer_epl': 39,
            'soccer_italy_serie_a': 135,
            'soccer_spain_la_liga': 140,
            'soccer_france_ligue_one': 61,
            'soccer_germany_bundesliga': 78,
            'soccer_sweden_allsvenskan': 113
        }

        for league_key, league_id in leagues.items():
            logging.info(f"Processing league: {league_key}")
            odds_data = self.fetch_upcoming_matches(league_key)
            if odds_data:
                self.save_odds_to_db(odds_data, league_key, leagues)

    def close_connection(self):
        """Close database connection."""
        logging.info("Closing database connection.")
        close_db_connection(self.conn, self.cursor)
