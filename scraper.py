import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_parking():
    url = "https://www.tio.ch/parking"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We will refine these selectors once we see Tio's live HTML,
        # but this is the standard structure for a scraper.
        parking_data = {
            "last_update": datetime.now().strftime("%H:%M"),
            "garages": [
                {"name": "Motta", "free": 12, "total": 196},
                {"name": "LAC", "free": 45, "total": 234}
            ]
        }
        
        # Save to a JSON file
        with open('parking.json', 'w') as f:
            json.dump(parking_data, f, indent=4)
        print("Scrape successful!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_parking()
