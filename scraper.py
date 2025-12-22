import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_parking():
    # We use the main parking page
    url = "https://www.lugano.ch/en/vivere-lugano/muoversi-lugano/posteggi/"
    
    headers = {
        'User-Agent': 'LuganoDashboardProject/1.0 (Hobby Project; contact: vizonarei@hotmail.com)',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        garages = []
        # Target list items that contain the word "spaces" or "Centro"
        items = soup.find_all('li')

        # Garages we want to track
        targets = ["Motta", "LAC", "Balestra", "Castello", "Bettydo", "Marzio", "Resega"]

        for item in items:
            text = item.get_text(separator='|').strip()
            # Example text format: "Motta - Centro | Free spaces: 12"
            
            for target in targets:
                if target.lower() in text.lower():
                    # Extract the numbers using a simple split/filter
                    parts = text.split('|')
                    free_val = 0
                    
                    for p in parts:
                        if "free" in p.lower() or "liberi" in p.lower() or "places" in p.lower():
                            # Find the first number in this string
                            nums = [int(s) for s in p.split() if s.isdigit()]
                            if nums:
                                free_val = nums[0]
                    
                    garages.append({
                        "name": target,
                        "free": free_val
                    })
                    break # Move to next list item

        # Remove duplicates and format
        unique_garages = {v['name']: v for v in garages}.values()
        
        data = {
            "last_update": datetime.now().strftime("%H:%M"),
            "garages": list(unique_garages)
        }
        
        # If we still found nothing, we need to know why
        if not data["garages"]:
            data["error"] = "No garage matches found in HTML list"

        with open('parking.json', 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        with open('parking.json', 'w') as f:
            json.dump({"error": "System Error", "details": str(e)}, f, indent=4)

if __name__ == "__main__":
    scrape_parking()
