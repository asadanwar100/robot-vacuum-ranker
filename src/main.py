from scraper.scrape_vacuumwars import scrape_vacuum_wars
from scraper.scrape_amazon import scrape_amazon

VW_URL = "https://vacuumwars.com/mova-v50-ultra-complete-review/"
AMAZON_URL = "https://www.amazon.com/Mova-Self-Cleaning-Navigation-Overcoming-DuoSolution/dp/B0F3WQTM9Q/"

print("--- Scraping VacuumWars ---")
scrape_vacuum_wars(VW_URL)

print("\n--- Scraping Amazon ---")
scrape_amazon(AMAZON_URL)