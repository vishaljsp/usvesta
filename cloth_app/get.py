import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_justdial(search_query, city, pages=2):
    results = []

    for page in range(1, pages + 1):
        url = f"https://www.justdial.com/{city}/{search_query}/page-{page}"
        print(f"Scraping: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        businesses = soup.find_all("li", class_="cntanr")

        for biz in businesses:
            try:
                name = biz.find("span", class_="lng_cont_name").text.strip()
            except:
                name = None

            try:
                phone = biz.find("p", class_="contact-info").get_text(strip=True)
            except:
                phone = None

            try:
                address = biz.find("span", class_="cont_fl_addr").text.strip()
            except:
                address = None

            if name:
                results.append({"Name": name, "Phone": phone, "Address": address})

    return results


if __name__ == "__main__":
    query = "Restaurants"   # yahan apna keyword daalo (Hotels, Gyms, Coaching, etc.)
    city = "Delhi"          # apna city daalo
    data = scrape_justdial(query, city, pages=3)

    # Save to Excel
    df = pd.DataFrame(data)
    df.to_excel("justdial_contacts.xlsx", index=False)
    print("✅ Data saved to justdial_contacts.xlsx")
