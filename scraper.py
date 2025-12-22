import requests
import json
from datetime import datetime

def scrape_parking():
    # The official Lugano City AJAX feed
    url = "https://www.lugano.ch/en/vivere-lugano/muoversi-lugano/posteggi/content/0.html?ajax=true&ajaxAction=stat"
    
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # The URL returns a list of dictionaries directly
        raw_data = response.json()
        
        # These are the garages we want to track
        target_garages = ["Motta", "LAC", "Balestra", "Castello", "Betty Do", "Campo Marzio", "Resega"]
        
        garages_to_save = []
        
        for item in raw_data:
            name = item.get('name', '').strip()
            
            # Check if this garage is in our target list
            if any(target in name for target in target_garages):
                garages_to_save.append({
                    "name": name,
                    "free": item.get('freeSlots', 0),
                    "total": item.get('slots', 0)
                })

        # Final Dashboard Package
        data = {
            "last_update": datetime.now().strftime("%H:%M"),
            "garages": garages_to_save
        }
        
        with open('parking.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("Success: Data saved to parking.json")
            
    except Exception as e:
        with open('parking.json', 'w') as f:
            json.dump({"error": "Failed to fetch Lugano API", "details": str(e)}, f, indent=4)

if __name__ == "__main__":
    scrape_parking()
