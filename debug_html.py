"""Debug script to inspect HTML structure of a fighter detail page."""
import requests
from bs4 import BeautifulSoup

resp = requests.get(
    'http://www.ufcstats.com/fighter-details/1338e2c7480bdf9e',
    headers={'User-Agent': 'Mozilla/5.0'}
)
soup = BeautifulSoup(resp.text, 'html.parser')

# Check for images
print("--- Images ---")
for img in soup.find_all('img'):
    src = img.get('src')
    cls = img.get('class')
    print(f"IMG src={src} class={cls}")

# Check for specific containers
profile = soup.find('div', class_='b-fighter-image')
if profile:
    print("Found 'b-fighter-image' div!")
else:
    print("No 'b-fighter-image' div.")
