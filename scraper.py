import datetime
import pytz # You might need to add this to your requirements/pip install

lugano_time = datetime.datetime.now(pytz.timezone('Europe/Zurich')).strftime('%H:%M')
# Then use lugano_time in your JSON 'last_update' field

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_parking():
    # This is the goldmine URL you found!
    url = "https://www.lugano.ch/vivere-lugano/muoversi-lugano/posteggi/content/0.html?ajax=true&ajaxAction=map"
    
    headers = {
        'User-Agent': 'LuganoDashboardProject/1.0 (Personal Hobby Project; contact: vizonarei@hotmail.com)',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        garages = []
        # Each garage is inside its own block. Usually, they start with <h5> names.
        blocks = soup.find_all(['h5']) 

        for block in blocks:
            name = block.get_text().strip()
            
            # Find the "Posteggi liberi" number that comes right after this name
            # We look at the parent container to find the text nearby
            container = block.find_parent()
            details = container.get_text(separator='|')
            
            # Split the text by the separator and look for the number after 'liberi'
            parts = [p.strip() for p in details.split('|')]
            
            free_val = None
            total_val = None
            
            for i, part in enumerate(parts):
                if "Posteggi liberi" in part:
                    # The number is usually the next part in the list
                    try:
                        free_val = int(parts[i+1])
                    except: pass
                if "Posteggi totali" in part:
                    try:
                        total_val = int(parts[i+1])
                    except: pass

            if free_val is not None:
                # Clean up names for your dashboard (e.g., "Motta - Centro" -> "Motta")
                short_name = name.split('-')[0].strip()
                garages.append({
                    "name": short_name,
                    "free": free_val,
                    "total": total_val
                })

        data = {
            "last_update": datetime.now().strftime("%H:%M"),
            "garages": garages
        }

        with open('parking.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Scrape Successful! Found {len(garages)} garages.")
            
    except Exception as e:
        with open('parking.json', 'w') as f:
            json.dump({"error": "Map Scrape Failed", "details": str(e)}, f, indent=4)

if __name__ == "__main__":
    scrape_parking()
