import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        content = page.content()
        browser.close()
        return content


def parse_product_page(html):
    soup = BeautifulSoup(html, "html.parser")

    # Product Title
    title_tag = soup.find("h1", {"class": "heading-5 v-fw-regular"})
    title = title_tag.get_text(strip=True) if title_tag else "N/A"

    # Price
    price_tag = soup.find("div", {"class": "priceView-hero-price priceView-customer-price"})
    price = price_tag.find("span").get_text(strip=True) if price_tag else "N/A"

    # Rating
    rating_tag = soup.find("span", {"class": "c-review-average"})
    rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

    # Reviews
    reviews = []
    review_tags = soup.find_all("p", {"class": "pre-white-space"}, limit=10)
    for tag in review_tags:
        text = tag.get_text(strip=True)
        if text:
            reviews.append(text)

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "reviews": reviews
    }


if __name__ == "__main__":
    url = "https://www.bestbuy.com/site/eufy-x10-pro-omni-wi-fi-connected-robot-vacuum-mop-with-self-washing-and-self-drying-auto-empty-station-black/6576392.p"
    html = fetch_html(url)
    print("HTML fetched")
    # Optional: Save to file for debugging
    with open("bestbuy_debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    data = parse_product_page(html)
    print(data)