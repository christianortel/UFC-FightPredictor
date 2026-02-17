"""
Runner script to scrape fighters S-Z to a separate file.
"""
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import scrape_all_fighters

if __name__ == "__main__":
    letters = ['s', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    print(f"Starting scraper for letters: {letters}")
    scrape_all_fighters(letters=letters, output_file="data/fighters_s_z.csv")
