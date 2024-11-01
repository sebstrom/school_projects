# fetch_match_results.py
import requests
import logging
import time
from datetime import datetime, timedelta
from db_connector import get_db_connection, close_db_connection

class MatchUpdater:
    def __init__(self, api_key):
        self.api_key = api_key
        self.conn, self.cursor = get_db_connection()
        logging.basicConfig(level=logging.DEBUG, filename='match_update_log.log',
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def fetch_match_data(self, match_id):
        """Fetch match result and statistics from API for a specific match_id."""
        url = f"https://v3.football.api-sports.io/fixtures?id={match_id}&include=statistics"
        headers = {'x-apisports-key': self.api_key}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('response', [])
        else:
            logging.error(f"Error fetching data for match {match_id}: {response.status_code}")
            return []

    def update_recent_match_results(self):
        """Update match results and statistics for matches in the last 10 days."""
        start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute("""
            SELECT match_id FROM matches 
            WHERE (home_score IS NULL OR away_score IS NULL) 
            AND date BETWEEN %s AND %s
        """, (start_date, end_date))
        matches_to_update = self.cursor.fetchall()

        logging.info(f"Found {len(matches_to_update)} matches to update.")

        for (match_id,) in matches_to_update:
            fixture_data = self.fetch_match_data(match_id)
            if fixture_data:
                fixture = fixture_data[0]
                home_score = fixture['goals']['home']
                away_score = fixture['goals']['away']

                # Process statistics if available
                if 'statistics' in fixture:
                    statistics = fixture['statistics']
                    # Lägg in statistiken i relevant databas här om det behövs

                # Uppdatera matchresultat
                try:
                    self.cursor.execute("""
                        UPDATE matches
                        SET home_score = %s, away_score = %s
                        WHERE match_id = %s
                    """, (home_score, away_score, match_id))
                    self.conn.commit()
                    logging.info(f"Match {match_id} updated with result {home_score}-{away_score}.")

                except Exception as e:
                    logging.error(f"Database update failed for match {match_id}: {e}")

            # Sömning för att begränsa anrop till max 10 per minut
            time.sleep(6)

    def close_connection(self):
        close_db_connection(self.conn, self.cursor)
