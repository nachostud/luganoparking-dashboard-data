import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_parking():
    # We switch back to the main page which is usually less strictly guarded than the API
    url = "https://www.lugano.ch/en/vivere-lugano/muoversi-lugano/posteggi/"
    
    headers = {
        'User-Agent': 'LuganoDashboardProject/1.0 (Hobby Project; contact: YOUR_EMAIL@HERE.com)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # If we didn't get HTML, something is wrong
        if "text/html" not in response.headers.get('Content-Type', ''):
            raise Exception(f"Unexpected Content-Type: {response.headers.get('Content-Type')}")

        soup = BeautifulSoup(response.text, 'html.parser')
        garages = []
        
        # This targets the specific "Parking" cards on the Lugano website
        # We look for any element containing the garage names
        targets = ["Motta", "LAC", "Balestra", "Castello", "Betty", "Marzio", "Resega"]
        
        # We search for the specific labels the site uses (e.g., "Free spaces")
        for target in targets:
            # Find the text "Motta", then look for the numbers near it
            element = soup.find(string=lambda t: t and target in t)
            if element:
                parent = element.find_parent()
                text_content = parent.get_text() if parent else ""
                
                # Logic to pull numbers (crude but effective)
                # We look for "Free spaces: X" or just the number next to the name
                import re
                nums = re.findall(r'\d+', text_content)
                if len(nums) >= 1:
                    garages.append({
                        "name": target,
                        "free": int(nums[0]),
                        "total": int(nums[1]) if len(nums) > 1 else 0
                    })

        data = {
            "last_update": datetime.now().strftime("%H:%M"),
            "garages": garages if garages else [{"name": "No Data", "free": 0}]
        }
        
        with open('parking.json', 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        # DEBUG: If it fails, we save the first 500 characters of the response 
        # so we can see if it's a "403 Forbidden" or "Cloudflare" block.
        error_msg = str(e)
        with open('parking.json', 'w') as f:
            json.dump({
                "error": "Scrape Failed",
                "details": error_msg,
                "timestamp": datetime.now().strftime("%H:%M")
            }, f, indent=4)

if __name__ == "__main__":
    scrape_parking()
