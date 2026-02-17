"""
Module to fetch fighter images from ufc.com on demand.
"""
import requests
from bs4 import BeautifulSoup
import re

def normalize_name_for_url(name):
    """
    Converts 'Sean O'Malley' to 'sean-omalley'.
    Removes special chars, lowercases, replaces spaces with hyphens.
    """
    # Remove dots (e.g. "C.M. Punk" -> "cm punk"?) No, usually "cm-punk"
    # UFC URL format is usually simple firstname-lastname
    
    # Lowercase
    name_lower = name.lower()
    
    # Replace " '" with "" (O'Malley -> omalley)
    name_lower = name_lower.replace("'", "")
    
    # Remove dots
    name_lower = name_lower.replace(".", "")
    
    # Replace spaces with hyphens
    normalized = re.sub(r'\s+', '-', name_lower)
    
    return normalized

def get_fighter_image_url(name):
    """
    Scrapes ufc.com to find the fighter's profile image.
    Returns URL or None.
    """
    slug = normalize_name_for_url(name)
    url = f"https://www.ufc.com/athlete/{slug}"
    
    try:
        # Timeout of 3s to not block UI too long
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
        if resp.status_code != 200:
            return None
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for the hero image
        # Class usually: 'hero-profile__image'
        img = soup.find('img', {'class': 'hero-profile__image'})
        
        if img and img.get('src'):
            src = img['src']
            # Sometimes parsing fields
            return src
            
    except Exception as e:
        print(f"Error fetching image for {name}: {e}")
        return None
    
    return None
