"""
Runner script to scrape fighters N-R (the missing gap) to a separate file.
"""
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import scrape_all_fighters

if __name__ == "__main__":
    letters = ['n', 'o', 'p', 'q', 'r']
    print(f"Starting scraper for letters: {letters}")
    scrape_all_fighters(letters=letters, output_file="data/fighters_n_r.csv")
