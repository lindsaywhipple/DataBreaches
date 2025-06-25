from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time

def wait_and_scroll(page, scroll_times=25, delay=1.5):
    for i in range(scroll_times):
        print(f"Scrolling {i+1}/{scroll_times}")
        page.mouse.wheel(0, 10000)
        time.sleep(delay)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://privacyrights.org/data-breaches")

    print("Waiting for page to load...")
    page.wait_for_timeout(5000)  # wait 5 sec to let Tableau load

    wait_and_scroll(page)

    # After scrolling is complete, capture page source
    html = page.content()

    browser.close()  # ✅ Only close after you're done scrolling

soup = BeautifulSoup(html, "html.parser")

# Placeholder: actual <tr> tag class may differ
rows = soup.find_all("tr")

breaches = []
for row in rows:
    cols = [td.get_text(strip=True) for td in row.find_all("td")]
    if len(cols) >= 9:
        breaches.append({
            "Month": cols[0],
            "Day": cols[1],
            "Year": cols[2],
            "Organization": cols[3],
            "Type": cols[4],
            "Total Affected": cols[5],
            "Residents Affected": cols[6],
            "State": cols[7],
            "Summary": cols[8]
        })

df = pd.DataFrame(breaches)
df["Date"] = df["Month"] + "/" + df["Day"] + "/" + df["Year"]
df.to_csv("prc_breach_tableau.csv", index=False)

print(f"✅ Done! {len(df)} rows saved to 'prc_breach_tableau.csv'")