import requests
from bs4 import BeautifulSoup
import json
import datetime
import pytz

def scrape_parking():
    url = "https://www.lugano.ch/vivere-lugano/muoversi-lugano/posteggi/content/0.html?ajax=true&ajaxAction=map"
    
    headers = {
        'User-Agent': 'LuganoDashboardProject/1.0 (Personal Hobby Project; contact: vizonarei@hotmail.com)',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        garages = []
        blocks = soup.find_all(['h5']) 

        for block in blocks:
            name = block.get_text().strip()
            container = block.find_parent()
            details = container.get_text(separator='|')
            parts = [p.strip() for p in details.split('|')]
            
            free_val = None
            total_val = None
            
            for i, part in enumerate(parts):
                if "Posteggi liberi" in part:
                    try:
                        free_val = int(parts[i+1])
                    except: pass
                if "Posteggi totali" in part:
                    try:
                        total_val = int(parts[i+1])
                    except: pass

            if free_val is not None:
                short_name = name.split('-')[0].strip()
                garages.append({
                    "name": short_name,
                    "free": free_val,
                    "total": total_val
                })

        # --- TIMEZONE FIX ---
        tz = pytz.timezone('Europe/Zurich')
        lugano_now = datetime.datetime.now(tz)
        current_time = lugano_now.strftime("%H:%M")

        data = {
            "last_update": current_time,
            "garages": garages
        }

        with open('parking.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Scrape Successful! Time: {current_time}. Found {len(garages)} garages.")
            
    except Exception as e:
        print(f"Error: {e}")
        # We don't want to overwrite the whole file with an error if it fails once
        # Better to let the old data stay than to break the dashboard

if __name__ == "__main__":
    scrape_parking()
