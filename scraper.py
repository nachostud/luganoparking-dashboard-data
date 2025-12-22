import requests
import json
import re
from datetime import datetime

def scrape_parking():
    url = "https://www.lugano.ch/en/vivere-lugano/muoversi-lugano/posteggi/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # We process the text to remove extra whitespace and make it one long string
        clean_text = " ".join(response.text.split())
        
        # We look for the garage name, then specifically the words "Free spaces" followed by a number
        # Example on site: "Motta - Centro ... Free spaces 12"
        targets = [
            ("Motta", "Motta"),
            ("LAC", "LAC"),
            ("Balestra", "Balestra"),
            ("Castello", "Castello"),
            ("Bettydo", "Bettydo"),
            ("Campo Marzio", "Marzio"),
            ("Resega", "Resega")
        ]
        
        garages_found = []

        for display_name, search_name in targets:
            # This regex is surgical: 
            # 1. Find the Name
            # 2. Skip up to 300 characters until we see "Free spaces" or "Posti liberi"
            # 3. Capture the very next digits
            pattern = rf"{search_name}.*?(?:Free spaces|Posti liberi|Places libres).*?(\d+)"
            match = re.search(pattern, clean_text, re.IGNORECASE)
            
            if match:
                garages_found.append({
                    "name": display_name,
                    "free": int(match.group(1))
                })

        data = {
            "last_update": datetime.now().strftime("%H:%M"),
            "garages": garages_found
        }
        
        # Fallback if surgical search fails: just look for the first number near the name
        if not garages_found:
            for display_name, search_name in targets:
                match = re.search(rf"{search_name}.*?(\d+)", clean_text, re.IGNORECASE)
                if match:
                    garages_found.append({"name": display_name, "free": int(match.group(1))})

        with open('parking.json', 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        with open('parking.json', 'w') as f:
            json.dump({"error": "Surgical Scrape Failed", "details": str(e)}, f, indent=4)

if __name__ == "__main__":
    scrape_parking()
