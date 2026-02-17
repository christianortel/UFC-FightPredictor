"""
UFC Fighter Stats Scraper
Scrapes fighter statistics from ufcstats.com
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
import string

BASE_URL = "http://www.ufcstats.com"
FIGHTERS_URL = f"{BASE_URL}/statistics/fighters"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def parse_height_to_cm(height_str):
    """Convert height string like 6' 4\" to cm."""
    if not height_str or height_str.strip() == '--':
        return None
    match = re.match(r"(\d+)'\s*(\d+)\"", height_str.strip())
    if match:
        feet = int(match.group(1))
        inches = int(match.group(2))
        return round((feet * 12 + inches) * 2.54, 1)
    return None

def parse_reach_to_cm(reach_str):
    """Convert reach string like 80\" to cm."""
    if not reach_str or reach_str.strip() == '--':
        return None
    match = re.match(r'(\d+)"', reach_str.strip())
    if match:
        return round(int(match.group(1)) * 2.54, 1)
    return None

def parse_percentage(pct_str):
    """Convert percentage string like '48%' to float 0.48."""
    if not pct_str or pct_str.strip() == '--':
        return None
    match = re.match(r'(\d+)%', pct_str.strip())
    if match:
        return int(match.group(1)) / 100.0
    return None

def parse_float(val_str):
    """Parse a float value, returning None for missing."""
    if not val_str or val_str.strip() == '--':
        return None
    try:
        return float(val_str.strip())
    except ValueError:
        return None

def parse_record(record_str):
    """Parse record string like 'Record: 24-5-0' into wins, losses, draws."""
    match = re.search(r'(\d+)-(\d+)-(\d+)', record_str)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return None, None, None

def parse_weight(weight_str):
    """Parse weight string like '185 lbs.' to int."""
    if not weight_str or weight_str.strip() == '--':
        return None
    match = re.match(r'(\d+)', weight_str.strip())
    if match:
        return int(match.group(1))
    return None

def get_fighter_urls(char):
    """Get all fighter detail URLs for a given letter."""
    url = f"{FIGHTERS_URL}?char={char}&page=all"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  Error fetching page for letter '{char}': {e}")
        return []
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Fighter links are in the table rows
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if '/fighter-details/' in href:
            links.add(href)
    
    return list(links)

def scrape_fighter_details(fighter_url):
    """Scrape a single fighter's detail page."""
    try:
        resp = requests.get(fighter_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  Error fetching {fighter_url}: {e}")
        return None
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    fighter = {}
    
    # Name
    name_tag = soup.find('span', class_='b-content__title-highlight')
    fighter['Name'] = name_tag.text.strip() if name_tag else 'Unknown'
    
    # Nickname
    nick_tag = soup.find('p', class_='b-content__Nickname')
    fighter['Nickname'] = nick_tag.text.strip() if nick_tag else ''
    
    # Record
    record_tag = soup.find('span', class_='b-content__title-record')
    if record_tag:
        wins, losses, draws = parse_record(record_tag.text)
        fighter['Wins'] = wins
        fighter['Losses'] = losses
        fighter['Draws'] = draws
    
    # Bio info (Height, Weight, Reach, Stance, DOB, career stats)
    bio_items = soup.find_all('li', class_='b-list__box-list-item')
    for item in bio_items:
        text = item.get_text(separator='|').strip()
        parts = [p.strip() for p in text.split('|') if p.strip()]
        if len(parts) >= 2:
            label = parts[0].rstrip(':').strip().lower()
            value = parts[-1].strip()
            
            if 'height' in label:
                fighter['Height_cm'] = parse_height_to_cm(value)
            elif 'weight' in label:
                fighter['Weight_lbs'] = parse_weight(value)
            elif 'reach' in label:
                fighter['Reach_cm'] = parse_reach_to_cm(value)
            elif 'stance' in label:
                fighter['Stance'] = value if value != '--' else None
            elif 'dob' in label:
                fighter['DOB'] = value if value != '--' else None
            elif 'slpm' in label:
                fighter['SLpM'] = parse_float(value)
            elif 'str. acc' in label:
                fighter['Str_Acc'] = parse_percentage(value)
            elif 'sapm' in label:
                fighter['SApM'] = parse_float(value)
            elif 'str. def' in label:
                fighter['Str_Def'] = parse_percentage(value)
            elif 'td avg' in label:
                fighter['TD_Avg'] = parse_float(value)
            elif 'td acc' in label:
                fighter['TD_Acc'] = parse_percentage(value)
            elif 'td def' in label:
                fighter['TD_Def'] = parse_percentage(value)
            elif 'sub. avg' in label:
                fighter['Sub_Avg'] = parse_float(value)
    
    fighter['URL'] = fighter_url
    return fighter

def scrape_all_fighters(letters=None, delay=0.15, output_file="data/fighters.csv"):
    """
    Scrape all fighters from ufcstats.com.
    letters: list of letters to scrape (default: all a-z)
    delay: seconds to wait between requests (be respectful)
    output_file: path to save the CSV
    """
    if letters is None:
        letters = list(string.ascii_lowercase)
    
    all_fighters = []
    total_urls = 0
    
    for char in letters:
        print(f"Fetching fighter list for letter '{char}'...")
        urls = get_fighter_urls(char)
        total_urls += len(urls)
        print(f"  Found {len(urls)} fighter URLs.")
        
        for i, url in enumerate(urls):
            fighter = scrape_fighter_details(url)
            if fighter and fighter.get('Name', 'Unknown') != 'Unknown':
                all_fighters.append(fighter)
            
            if (i + 1) % 20 == 0:
                print(f"  Scraped {i + 1}/{len(urls)} fighters for '{char}'...")
                # Save incrementally every 20 fighters
                temp_df = pd.DataFrame(all_fighters)
                os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
                temp_df.to_csv(output_file, index=False)
            
            time.sleep(delay)
        
        print(f"  Done with '{char}'. Total fighters so far: {len(all_fighters)}")
        
        # Save incrementally
        temp_df = pd.DataFrame(all_fighters)
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        temp_df.to_csv(output_file, index=False)
    
    return pd.DataFrame(all_fighters)

if __name__ == "__main__":
    import sys
    
    # Allow passing specific letters as argument for testing
    # e.g., python src/scraper.py a b c
    if len(sys.argv) > 1:
        letters = [l.lower() for l in sys.argv[1:]]
    else:
        letters = None  # All letters
    
    df = scrape_all_fighters(letters=letters)
    if df is not None:
        print(f"\nSample data:")
        print(df[['Name', 'Wins', 'Losses', 'Height_cm', 'Reach_cm', 'SLpM', 'TD_Avg']].head(10))
