import requests
import json
from datetime import datetime

def scrape_parking():
    # The official Lugano City AJAX feed
    url = "https://www.lugano.ch/en/vivere-lugano/muoversi-lugano/posteggi/content/0.html?ajax=true&ajaxAction=stat"
    
    # STEALTH + RESPONSIBLE HEADERS
    # We identify ourselves politely while providing the 'Referer' the server expects.
    headers = {
        'User-Agent': 'LuganoDashboardProject/1.0 (Personal Hobby Project; contact: vizonarei@hotmail.com)',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.lugano.ch/en/vivere-lugano/muoversi-lugano/posteggi/',
    }
    
    try:
        # Using a session is more 'polite' as it reuses the connection
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        # Raise an error if we didn't get a 200 OK response
        response.raise_for_status()

        # Parse the JSON from the city
        raw_data = response.json()
        
        # Mapping our preferred display names to what is actually in the data
        # 'Betty Do' and 'Campo Marzio' often have slight spelling variations in the feed
        target_names = ["Motta", "LAC", "Balestra", "Castello", "Betty Do", "Campo Marzio", "Resega"]
        garages_to_save = []
        
        for item in raw_data:
            name = item.get('name', '').strip()
            
            # Check if this name matches any of our targets
            if any(target in name for target in target_names):
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
        print("Scrape Successful: parking.json updated.")
            
    except Exception as e:
        # Log the error into the JSON so the ESP32 can tell us what went wrong
        error_data = {
            "last_update": datetime.now().strftime("%H:%M"),
            "error": "Failed to fetch data",
            "details": str(e)
        }
        with open('parking.json', 'w') as f:
            json.dump(error_data, f, indent=4)
        print(f"Scrape Failed: {e}")

if __name__ == "__main__":
    scrape_parking()
