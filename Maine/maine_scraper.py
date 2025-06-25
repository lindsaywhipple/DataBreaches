import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://www.maine.gov"
LIST_URL = f"{BASE_URL}/agviewer/content/ag/985235c7-cb95-4be2-8792-a1252b4f8318/list.html"
DETAIL_PREFIX = f"{BASE_URL}/agviewer/content/ag/985235c7-cb95-4be2-8792-a1252b4f8318/"

def fetch_main_entries():
    res = requests.get(LIST_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("table tr")[1:]

    entries = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) != 2:
            continue
        date_reported = cols[0].text.strip()
        link_tag = cols[1].find("a")
        if not link_tag:
            continue
        org_name = link_tag.text.strip()
        detail_href = link_tag['href']
        detail_url = DETAIL_PREFIX + detail_href.split('/')[-1]
        entries.append({
            "Organization": org_name,
            "Date Reported": date_reported,
            "Detail URL": detail_url
        })
    return entries

def parse_detail_page(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    
    def extract_strong_text(label):
        for li in soup.select("ul.plain li"):
            if label in li.text:
                strong = li.find("strong")
                return strong.text.strip() if strong else ""
        return ""

    def extract_nested_breach_type():
        breach_section = soup.find("li", string=lambda t: t and "Description of the Breach" in t)
        if breach_section:
            nested = breach_section.find_next("ul")
            if nested:
                item = nested.find("li")
                return item.text.strip() if item else ""
        return ""

    def extract_pdf_link():
        for a in soup.select("a[href$='.pdf']"):
            return BASE_URL + a['href']
        return ""

    return {
        "Industry": extract_strong_text("Type of Organization:"),
        "Date of Incident": extract_strong_text("Date(s) Breach Occured:"),
        "Date of Discovery": extract_strong_text("Date Breach Discovered:"),
        "Residents Affected": extract_strong_text("Total number of Maine residents affected:"),
        "Breach Type": extract_nested_breach_type(),
        "PDF Link": extract_pdf_link()
    }

def main():
    entries = fetch_main_entries()
    full_data = []

    for entry in entries:
        try:
            details = parse_detail_page(entry["Detail URL"])
            full_data.append({
                "Organization": entry["Organization"],
                "Date Reported": entry["Date Reported"],
                "Industry": details["Industry"],
                "Date of Incident": details["Date of Incident"],
                "Date of Discovery": details["Date of Discovery"],
                "Residents Affected": details["Residents Affected"],
                "Breach Type": details["Breach Type"],
                "PDF Link": details["PDF Link"],
                "Detail URL": entry["Detail URL"]
            })
            time.sleep(0.5)
        except Exception as e:
            full_data.append({
                "Organization": entry["Organization"],
                "Date Reported": entry["Date Reported"],
                "Industry": "ERROR",
                "Date of Incident": "",
                "Date of Discovery": "",
                "Residents Affected": "",
                "Breach Type": f"Error: {e}",
                "PDF Link": "",
                "Detail URL": entry["Detail URL"]
            })

    with open("maine_data_breaches.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=full_data[0].keys())
        writer.writeheader()
        writer.writerows(full_data)

if __name__ == "__main__":
    main()