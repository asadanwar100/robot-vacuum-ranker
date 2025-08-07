# test_playwright_bestbuy.py

from playwright.sync_api import sync_playwright
import time

import time
from playwright.sync_api import sync_playwright

def fetch_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Keep it visible for debugging
        page = browser.new_page()
        print(f"Navigating to: {url}")

        try:
            # 1. More robust initial page load
            # 'domcontentloaded': Waits for the initial HTML to be parsed.
            # 'load': Waits for all resources (images, stylesheets) to finish loading.
            # 'networkidle': Waits until there are no network connections for at least 500 ms.
            # Best Buy is very dynamic, so 'networkidle' is often the most effective,
            # though it can be slower. You might need to experiment.
            page.goto(url, wait_until="networkidle", timeout=60000) # Increased timeout to 60 seconds
            print("Page navigated. Waiting for elements...")

            # 2. Wait for a more indicative element of content loading
            # Best Buy product pages often have a "Specifications" section or similar.
            # Find a common selector for detailed product info or the main content area.
            # I'm using a common Best Buy product page structure selector.
            # You might need to inspect the specific page you're targeting to find
            # the most reliable selector for its fully loaded state.
            # Example: "div.model-specs", "div.data-display-label", etc.
            # I'll use a general approach first, then more specific if needed.
            # For robot vacuums, often a spec table or key features list is present.
            try:
                page.wait_for_selector(".specs-accordion-container", timeout=15000) # Common for specs
                print("✅ Specifications container found.")
            except Exception:
                print("⚠️ Specifications container not found, trying other elements...")
                try:
                    page.wait_for_selector(".shop-sku-list-item", timeout=15000) # For product list pages
                    print("✅ Product list item found.")
                except Exception:
                    print("⚠️ No main content selector found, page might be incomplete.")

            # 3. Explicitly wait for the reviews section to appear, if applicable
            # Best Buy uses a dynamically loaded module for reviews.
            # It's usually within an iframe or loaded via API.
            # Look for a common selector for the reviews section, e.g., a heading or a review summary.
            # You might need to inspect the Best Buy reviews section carefully.
            try:
                # This selector is a common pattern for review sections on Best Buy
                page.wait_for_selector("div[data-comp='ProductReviewSummary']", timeout=15000)
                print("✅ Review summary section found.")
            except Exception:
                print("⚠️ Review summary section not found. Reviews might not have loaded or don't exist.")

            # 4. Scroll to bottom more effectively and repeatedly
            # Best Buy sometimes uses infinite scroll or lazy loading for content like more reviews.
            # You'll want to keep scrolling until the scroll height stops changing.
            print("Scrolling to load all dynamic content...")
            previous_scroll_height = -1
            max_scroll_attempts = 10 # Limit attempts to prevent infinite loops

            for i in range(max_scroll_attempts):
                current_scroll_height = page.evaluate("document.body.scrollHeight")
                if current_scroll_height == previous_scroll_height:
                    print(f"Scroll height stabilized after {i} attempts.")
                    break
                previous_scroll_height = current_scroll_height
                page.mouse.wheel(0, current_scroll_height) # Scroll to the very bottom
                time.sleep(1.5) # Give content time to load after scroll

            # 5. Wait a final moment for any last-minute JavaScript rendering
            time.sleep(3)

            html = page.content()
            print("HTML content captured.")
            return html

        except Exception as e:
            print(f"An error occurred: {e}")
            # You might want to save a screenshot here for debugging failed loads
            # page.screenshot(path="failed_load.png")
            return None
        finally:
            browser.close()
            print("Browser closed.")

# Example Usage:
# Replace with an actual Best Buy product page URL for a robot vacuum/mop
# For example: url = "https://www.bestbuy.com/site/roborock-s8-pro-ultra-robot-vacuum-and-mop-with-rockdock-ultra-white/6536551.p?skuId=6536551"
# or another robot vacuum listing page:
# url = "https://www.bestbuy.com/site/robot-vacuums-mops/robot-vacuums/pcmcat341600050014.c?id=pcmcat341600050014"

# def fetch_html(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # Keep it visible for debugging
#         page = browser.new_page()
#         print("Navigating...")
#         page.goto(url, timeout=30000)

#         # Wait for product title (proof that page is mostly loaded)
#         try:
#             page.wait_for_selector("h1.heading-5", timeout=10000)
#         except Exception:
#             print("⚠️ Title not found.")

#         # Scroll to bottom to force review section to load
#         print("Scrolling...")
#         for _ in range(5):  # Scroll in steps
#             page.mouse.wheel(0, 2000)
#             time.sleep(1)

#         # Wait a moment to let reviews render
#         time.sleep(2)

#         html = page.content()
#         browser.close()
#         return html
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=False)
    #     page = browser.new_page()
    #     print("Navigating...")
    #     page.goto(url, timeout=30000)  # 30s timeout
    #     # 👇 Wait for a known element to appear (title)
    #     try:
    #         page.wait_for_selector("h1.heading-5", timeout=100000)
    #         print("Page loaded.")
    #     except Exception:
    #         print("⚠️ Page did not fully load required content.")   
    #     html = page.content()
    #     browser.close()
    #     return html

if __name__ == "__main__":
    url = "https://www.bestbuy.com/site/eufy-x10-pro-omni-wi-fi-connected-robot-vacuum-mop-with-self-washing-and-self-drying-auto-empty-station-black/6576392.p"
    html = fetch_html(url)

    with open("bestbuy_playwright_debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Done. HTML saved to file.")