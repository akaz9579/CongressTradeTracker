from bs4 import BeautifulSoup as BS
import requests

"""TODO: Start Version 1.0"""

page_to_scrape = requests.get("https://www.capitoltrades.com/trades?assetType=stock&assetType=crypto")
soup = BS(page_to_scrape.text, "html.parser")
quotes = soup.find_all("a", attrs = {"class": "text-txt-interactive"})

for quote in quotes:
    print(quote.text)