from playwright.sync_api import sync_playwright, TimeoutError
import pandas as pd
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright_stealth import Stealth



def scrape_amazon_product_page(url: str, user_data_dir) -> dict | None:
    """
    Navigates to an Amazon product page, extracts key information,
    and returns it as a dictionary.

    Args:
        url: The full URL of the Amazon product page.

    Returns:
        A dictionary containing the scraped data, or None if an error occurs.
    """
   
    with sync_playwright() as p:
        # Launch a persistent browser context from the specified directory
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=['--disable-blink-features=AutomationControlled'], # Disguises the browser further
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}, # Set a realistic viewport size
            slow_mo=50 # Adds a small delay to mimic human interaction speed
        )
        page = context.new_page()

        try:
            stealth = Stealth()
            stealth.apply_stealth_sync(page)
            print(f"Navigating to Amazon URL: {url}")
            # Use 'load' to wait for all resources, which is safer for complex pages
            page.goto(url, wait_until="load", timeout=60000)

            # Check for CAPTCHA - a common reason for failure
            if "captcha" in page.title().lower():
                print("CAPTCHA detected. Saving screenshot and aborting.")
                page.screenshot(path="amazon_captcha_error.png")
                return None

            # --- Wait for a key element to ensure the page is ready ---
            print("Waiting for main product content to load...")
            page.wait_for_selector('span#productTitle', timeout=15000)

            # --- Extract Core Information ---
            product_title = page.locator('span#productTitle').inner_text().strip()
            print(f"Found product: {product_title}")

            # Price Extraction
            price = None
            try:
                price_locator = page.locator('.a-price .a-offscreen').first
                price_locator.wait_for(state="visible", timeout=5000)
                price_text = price_locator.inner_text()
                price = float(price_text.replace('$', '').replace(',', ''))
                print(f"Price found: {price}")
            except TimeoutError:
                print("Price element did not become visible.")
            
            # Star Rating
            star_rating = None
            try:
                rating_locator = page.locator('#averageCustomerReviews_feature_div #acrPopover')
                rating_locator.wait_for(state="visible", timeout=5000)
                rating_text = rating_locator.get_attribute('title')
                star_rating = float(rating_text.split(' ')[0])
                print(f"Rating found: {star_rating}")
            except TimeoutError:
                print("Star rating element did not become visible.")


            # --- Extract Customer Reviews ---
            print("Extracting customer reviews...")
            # This locator finds the text spans within the review section
            review_elements = page.locator('span[data-hook="review-body"] span')
            reviews = [element.inner_text() for element in review_elements.all()]

            # --- Assemble the Final Data Object ---
            scraped_data = {
                "model_name": product_title,
                "source": "Amazon",
                "url": url,
                "scraped_timestamp": datetime.utcnow().isoformat() + "Z",
                "manufacturer_specs": {
                    "price": price,
                },
                "customer_feedback": {
                    "average_star_rating": star_rating,
                    "reviews_text": reviews[:20] # Limit to the first 20 reviews found
                }
            }

            return scraped_data

        except TimeoutError:
            print(f"Timeout Error: A key element did not appear for {url}. The page may be a captcha or have a different layout.")
            page.screenshot(path="amazon_error.png") # Save a screenshot for debugging
            return None
        except Exception as e:
            print(f"An unexpected error occurred for {url}: {e}")
            return None
        finally:
            print("Closing browser.")
            context.close()

def scrape_amazon(url):
    # Replace with a real Amazon URL
    # test_url = "https://www.amazon.com/Mova-Self-Cleaning-Navigation-Overcoming-DuoSolution/dp/B0F3WQTM9Q/"
    # Create a directory to store the browser session data
    user_data_path = Path("./playwright_user_data")
    user_data_path.mkdir(exist_ok=True)


    amazon_data = scrape_amazon_product_page(url, user_data_path)

    if amazon_data:
        # Now, save it using the partitioned file structure
        model_name_clean = amazon_data['model_name'].replace(' ', '_').replace('/', '').lower()[:50] # Truncate long names
        file_name = f"{model_name_clean}_amazon.json"
        
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        script_dir = Path(__file__).parent
        proj_dir = script_dir.parent.parent
        output_path = proj_dir / "data" / "raw" / "amazon" / today_str
        output_path.mkdir(parents=True, exist_ok=True)
        full_file_path = output_path / file_name

        with open(full_file_path, 'w') as f:
            json.dump(amazon_data, f, indent=4)
        print(f"\nSuccessfully scraped and saved data to: {full_file_path}")


