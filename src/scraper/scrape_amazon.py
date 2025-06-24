import requests
from bs4 import BeautifulSoup

def fetch_product_page(url):
    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
    response = requests.get(url,headers=headers)
    return response.text

def extract_title_and_reviews(html):
    soup = BeautifulSoup(html,"html.parser")
    data = {}

    #Title
    title = soup.find(id="productTitle")
    data["title"] = title.get_text(strip=True) if title else None

    #Price
    price = soup.find("span", class_="a-offscreen")    
    data["price"] = price.get_text(strip=True) if price else None

    #Rating
    rating = soup.find("span", class_="a-icon-alt")
    data["rating"] = rating.get_text(strip=True) if rating else None

    #Reviews
    reviews = []
    review_blocks = soup.find_all("span",{"data_hook": "review_body"})
    for r in review_blocks[:10]:
        reviews.append(r.get_text(strip=True))
    data["reviews"] = reviews

    return (data)

if __name__ == "__main__":
    url = "https://www.amazon.com/iRobot-Roomba-Combo-Vacuum-AutoWash/dp/B0DWG1YNJR/"
    html = fetch_product_page(url)
    
    data = extract_title_and_reviews(html)
    for k in data:
        print(f"{k}: {data[k]}")