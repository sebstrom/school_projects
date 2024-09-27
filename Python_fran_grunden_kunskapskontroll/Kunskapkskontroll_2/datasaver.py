import logging
import sqlite3

class DataSaver:
    """Class to save data to SQL table."""
    
    def __init__(self, db="odds_data.db") -> None:
        self.logger = logging.getLogger(__name__)
        self.db = db 

    def save_data(self, data):
        """Saves cleaned data to the SQL table."""
        self.logger.info("Saving data...")
        
        # try with so it disconnect automatically 
        try:
            with sqlite3.connect(self.db) as connection:
                cursor = connection.cursor()
                
                # Create table if it does not already exist 
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS odds_data (
                        id INTEGER PRIMARY KEY,
                        home_team TEXT,
                        away_team TEXT,
                        home_odds DECIMAL,
                        draw_odds DECIMAL,
                        away_odds DECIMAL
                    )
                ''')
                self.logger.info("Table 'odds_data' created or already exists.")
                
                # Save the data
                for match in data:
                    cursor.execute('''
                        INSERT OR IGNORE INTO odds_data (home_team, away_team, home_odds, draw_odds, away_odds)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (match["home_team"], match["away_team"], match["home_odds"], match["draw_odds"], match["away_odds"]))
                
                self.logger.info("Data saved successfully.")
        # Catch potential errors with except         
        except sqlite3.Error as e:
            self.logger.error(f"Error saving data: {e}")
