import requests
import json
import re
from datetime import datetime

def scrape_parking():
    # Primary URL for the main parking status
    url = "https://www.lugano.ch/en/vivere-lugano/muoversi-lugano/posteggi/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # We grab the entire text content of the page
        full_text = response.text
        
        # Garages we want to find
        targets = ["Motta", "LAC", "Balestra", "Castello", "Bettydo", "Marzio", "Resega"]
        garages_found = []

        # We look for the garage name and then the nearest number following the word "spaces" or "liberi"
        for target in targets:
            # This Regex looks for: [Garage Name] ... [Any words] ... [Number]
            # It's very broad to catch variations in the site layout
            pattern = rf"{target}.*?(?:spaces|liberi|places|Plätze|Posti).*?(\d+)"
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            
            if match:
                free_val = int(match.group(1))
                garages_found.append({
                    "name": target,
                    "free": free_val
                })
        
        # If the specific regex fails, let's try a simpler 'Find near name' logic
        if not garages_found:
            for target in targets:
                # Find the name and just grab the next number within 100 characters
                pattern_simple = rf"{target}.*?(\d+)"
                match_simple = re.search(pattern_simple, full_text, re.IGNORECASE | re.DOTALL)
                if match_simple:
                    garages_found.append({
                        "name": target,
                        "free": int(match_simple.group(1))
                    })

        data = {
            "last_update": datetime.now().strftime("%H:%M"),
            "garages": garages_found
        }
        
        if not garages_found:
            data["error"] = "Zero garages matched. Content length: " + str(len(full_text))

        with open('parking.json', 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        with open('parking.json', 'w') as f:
            json.dump({"error": "Final Attempt Failed", "details": str(e)}, f, indent=4)

if __name__ == "__main__":
    scrape_parking()
