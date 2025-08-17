import time
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime, timezone
import json
from pathlib import Path

def get_vacuum_wars_ratings(url: str) -> pd.DataFrame | None:
    """
    Fetches the ratings table from a Vacuum Wars page using only Playwright locators
    and Pandas for table parsing.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        try:
            # Action 1: Navigate to the page
            print(f"Navigating to {url}...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Action 2: Locate the specific container div
            print("Looking for the 'Vacuum Wars Ratings' section...")
            # This robust selector finds the div that contains the target text
            accordion_item = page.locator('div.gb-accordion__item:has-text("Vacuum Wars Ratings")')

            if accordion_item.count() == 0:
                print("Could not find the 'Vacuum Wars Ratings' container div.")
                return None

            # Action 3: Extract the HTML from that specific element
            print("Section found. Extracting its HTML...")
            container_html = accordion_item.inner_html()

            # Action 4: Parse the extracted HTML with Pandas
            tables = pd.read_html(container_html)
            if not tables:
                print("No table found within the container.")
                return None
            
            ratings_df = tables[0]
            print("Successfully parsed the table!")
            return ratings_df

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            browser.close()

def convert_and_save_json(ratings_df: pd.DataFrame):
    """
    Converts the Vacuum Wars ratings DataFrame to a structured JSON object
    and saves it to a file.
    """
    if ratings_df is None or ratings_df.empty:
        print("Input DataFrame is empty. Cannot convert to JSON.")
        return

    try:
        # --- Step 1: Extract the model name from the second column header ---
        model_name = ratings_df.columns[1]
        file_name = f"{model_name.replace(' ','_').lower()}_vw_ratings.json"

        # --- Step 2: Set the first column as the index for easy conversion ---
        # This makes the test names (e.g., 'Features') the keys in our dictionary.
        df = ratings_df.set_index(ratings_df.columns[0])

        # --- Step 3: Select just the scores and convert to a dictionary ---
        # We select the column with the model name, which now contains all the scores.
        scores_dict = df[model_name].to_dict()

        # --- Step 4: Assemble the final JSON structure ---
        # This structure is clean and matches our BigQuery schema plan.
        output_data = {
            "model_name": model_name.strip(),
            "source": "VacuumWars",
            "scraped_timestamp": datetime.now(timezone.utc).isoformat() + "Z", # Add timestamp
            "expert_scores": scores_dict
        }

        # --- Step 5: Save the dictionary to a JSON file ---
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        script_dir = Path(__file__).parent
        proj_dir = script_dir.parent.parent
        output_path = proj_dir / "data" / "raw" / "vacuum_wars" / today_str
        output_path.mkdir(parents=True, exist_ok=True)
        full_file_path = output_path / file_name

        with open(full_file_path, 'w') as f:
            json.dump(output_data, f, indent=4)
        
        print(f"Successfully saved data for '{model_name}' to {full_file_path}")
        
    except (IndexError, KeyError) as e:
        print(f"Error processing DataFrame. Check column structure: {e}")


def scrape_vacuum_wars(url):
    test_url="https://vacuumwars.com/mova-v50-ultra-complete-review/"
    ratings_data = get_vacuum_wars_ratings(test_url)

    if ratings_data is not None:
        print("\n--- Extracted DataFrame ---")
        print(ratings_data)

    convert_and_save_json(ratings_data)
   