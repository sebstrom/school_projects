import logging

class DataCleaner:
    """A class to clean data and logg the information"""
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        
    def clean_data(self, odds_data):
        cleaned_data = []
        # try to clean the data
        for i, match in enumerate(odds_data):
            try:
                # Get the teams name
                home_team = match.get("home_team", "N/A")
                away_team = match.get("away_team", "N/A")

                # Get the odds
                outcomes = match.get("bookmakers", [{}])[0].get("markets", [{}])[0].get("outcomes", [])
                odds_dict = {outcome['name']: outcome['price'] for outcome in outcomes}

                cleaned_match = {
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_odds": odds_dict.get(home_team, 0), 
                    "draw_odds": odds_dict.get('Draw', 0),
                    "away_odds": odds_dict.get(away_team, 0)  
                }
                
                # Checking missing odds
                if cleaned_match["home_odds"] == 0 or cleaned_match["draw_odds"] == 0 or cleaned_match["away_odds"] == 0:
                    self.logger.warning(f"Missing odds for match {i + 1}: {home_team} vs {away_team}")

                cleaned_data.append(cleaned_match)

            except (IndexError, KeyError) as e:
                # Logging errors 
                self.logger.error(f"Error cleaning match {i + 1}: {e}")
                
        self.logger.info(f"Data cleaning successful, total cleaned matches: {len(cleaned_data)}")
        return cleaned_data
