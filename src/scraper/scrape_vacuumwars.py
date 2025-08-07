import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

def fetch_html(url, wait_until="domcontentloaded", timeout=30000):
    """
    General function to fetch HTML content from a URL using Playwright.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Can be headless for Vacuum Wars
        page = browser.new_page()
        try:
            print(f"Navigating to: {url}")
            page.goto(url, wait_until=wait_until, timeout=timeout)
            time.sleep(1) # Small pause to ensure rendering
            html = page.content()
            print("HTML content captured.")
            return html
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
        finally:
            browser.close()

def get_vacuumwars_review_urls(sitemap_url="https://vacuumwars.com/sitemap/"):
    """
    Fetches the Vacuum Wars sitemap and extracts URLs for review articles.
    """
    html = fetch_html(sitemap_url)
    if not html:
        return []
    
    with open("vacuumwars_playwright_debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, 'html.parser')
    review_urls = set()

    # Look for links within the 'Reviews' section or direct article links
    # You'll need to inspect the sitemap's HTML structure for the best selectors.
    # From a quick look, many review links are direct children of <ul> within specific sections.

    # This is a generic approach; refine selectors after inspecting the sitemap HTML.
    # A good starting point would be to find the main content area and then all 'a' tags within it.
    # main_content = soup.find('div', class_=re.compile(r'sitemap-content|main-content')) # Adjust class as needed
    main_content = soup.find('div', id='ocs-site') # Adjust class as needed
    if main_content:
        for link in main_content.find_all('a', href=True):
            href = link['href']
            # Filter for URLs that look like review articles (e.g., containing 'review' or part of a guide)
            if "vacuumwars.com/" in href and (
                "/review/" in href or
                "/guide/" in href or
                "best-robot-vacuums" in href # For the main comparison page
            ):
            # ) and not href.endswith('/'): # Avoid adding duplicates for base paths
                review_urls.add(href.split('#')[0]) # Remove anchor links

    # You might also find URLs directly in an XML sitemap, which is even easier to parse.
    # Check for https://vacuumwars.com/sitemap.xml
    # If it exists, that's often cleaner than HTML parsing.
    # For now, sticking with HTML sitemap.

    return sorted(list(review_urls))

# Example Usage:
review_pages = get_vacuumwars_review_urls()
print(f"Found {len(review_pages)} potential review URLs.")
for i, url in enumerate(review_pages[:10]): # Print first 10
    print(url)