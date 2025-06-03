import time 
from playwright.sync_api import sync_playwright

"""TODO: Start Version 1.0"""


'Essensially Read the page, see trades being done by politicans'
url = 'https://www.capitoltrades.com/trades?assetType=stock&assetType=crypto&assetType=etf&page=1&txDate=365d'
    
pW = sync_playwright().start()
browser = pW.webkit.launch(headless=False)

page = browser.new_page(
    java_script_enabled=True,
    viewport={'width': 1920, 'height': 1000}
)

page.goto(url, wait_until='load')

page.wait_for_timeout(5000)  # wait for content to load

# Example: get all trade rows (you'll inspect to get the exact selectors)
rows = page.query_selector_all("selector-for-each-trade")

data = []
for row in rows:
    name = row.query_selector("selector-for-name").inner_text()
    ticker = row.query_selector("selector-for-ticker").inner_text()
    date = row.query_selector("selector-for-date").inner_text()
    size = row.query_selector("selector-for-size").inner_text()
    price = row.query_selector("selector-for-price").inner_text()
    type = row.query_selector("selector-for-buy-sell").inner_text()

    data.append({
        "name": name,
        "ticker": ticker,
        "date": date,
        "type": type,
        "size": size,
        "price": price
    })

browser.close()
print(data)