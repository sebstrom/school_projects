import pytest
from datacleaner import DataCleaner 

@pytest.fixture
def data_cleaner():
    """Fixture to create a DataCleaner instance."""
    return DataCleaner()

@pytest.fixture
def valid_odds_data():
    """Provides data that should be valid."""
    return [
        {
            "home_team": "Linus Hjältar",
            "away_team": "Antonios Undersåtar",
            "bookmakers": [
                {
                    "markets": [
                        {
                            "outcomes": [
                                {"name": "Linus Hjältar", "price": 1.5},
                                {"name": "Draw", "price": 2.1},
                                {"name": "Antonios Undersåtar", "price": 2.3}
                            ]
                        }
                    ]
                }
            ]
        }
    ]

# Test to see if it is cleaned and works correctly
def test_valid_odds(data_cleaner, valid_odds_data):
    cleaned_data = data_cleaner.clean_data(valid_odds_data)
    
    assert len(cleaned_data) == 1 
    assert cleaned_data[0]["home_team"] == "Linus Hjältar"
    assert cleaned_data[0]["away_team"] == "Antonios Undersåtar"
    assert cleaned_data[0]["home_odds"] == 1.5
    assert cleaned_data[0]["draw_odds"] == 2.1
    assert cleaned_data[0]["away_odds"] == 2.3


# Try with invalid odds 


@pytest.fixture
def no_outcomes():
    """Test data where there is no outcome."""
    return [
        {
            "home_team": "Sebbes Favoriter",
            "away_team": "Dom Onda",
            "bookmakers": [
                {
                    "markets": [
                        {
                            "outcomes": []
                        }
                    ]
                }
            ]
        }
    ]

@pytest.fixture
def odds_zero():
    """Test data where odds are zero."""
    return [
        {
            "home_team": "Sebbes Favoriter",
            "away_team": "Dom Onda",
            "bookmakers": [
                {
                    "markets": [
                        {
                            "outcomes": [
                                {"name": "Sebbes Favoriter", "price": 0},
                                {"name": "Draw", "price": 0},
                                {"name": "Dom Onda", "price": 0}
                            ]
                        }
                    ]
                }
            ]
        }
    ]


def test_bad_data(data_cleaner, no_outcomes):
    """Test to raise exception if there is no outcome"""
    with pytest.raises(ValueError):
        data_cleaner.clean_data(no_outcomes)

def test_bad_data(data_cleaner, odds_zero):
    """Test to raise exception if odds is zero"""
    with pytest.raises(ValueError):
        data_cleaner.clean_data(odds_zero)


        
        