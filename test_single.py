"""Quick test: scrape a single fighter and print all extracted fields."""
import sys
sys.path.insert(0, '.')
from src.scraper import scrape_fighter_details

url = 'http://www.ufcstats.com/fighter-details/1338e2c7480bdf9e'  # Adesanya
print("Scraping Israel Adesanya...")
fighter = scrape_fighter_details(url)
if fighter:
    for k, v in fighter.items():
        print(f"  {k}: {v}")
else:
    print("Failed to scrape fighter.")
