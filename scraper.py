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
        
        garages = []
        
        # Tio.ch lists parking in a table or list. 
        # We look for the common row structure they use.
        # Note: If Tio change their layout, we just update these 3 lines.
        items = soup.select('.parking-list-item, tr') 

        for item in items:
            text = item.get_text(separator='|').strip()
            parts = [p.strip() for p in text.split('|') if p.strip()]
            
            # We look for rows that have a name and a number
            if len(parts) >= 2:
                name = parts[0]
                # Filter for the garages you care about
                if name in ["Motta", "LAC", "Balestra", "Castello", "Bettydo", "C. Marzio", "Resega"]:
                    # Clean up the numbers (Tio usually shows 'Free / Total')
                    status = parts[1] 
                    garages.append({"name": name, "free": status})

        # Final Data Package
        data = {
            "last_update": datetime.now().strftime("%H:%M"),
            "garages": garages if garages else [{"name": "Error", "free": "Check Scraper"}]
        }
        
        with open('parking.json', 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        print(f"Scrape failed: {e}")

if __name__ == "__main__":
    scrape_parking()
