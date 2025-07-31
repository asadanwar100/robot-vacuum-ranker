Project Scope: AI-Powered Robot Vacuum Ranking Engine (Version 1.0 - MVP)

Mission Statement (MVP)
This project's MVP will be a web application that ranks a curated list of robot vacuums based on a weighted scoring model. The initial data will be scraped from VacuumWars and Amazon. The user will be able to apply a price filter and then assign importance weights to the following specific criteria:
Quantitative Performance (from VacuumWars):
Carpet Deep Clean Score
Hard Floor Pickup Score
Qualitative Performance (from Amazon Reviews via ABSA):
Sentiment on "Battery Life"
Sentiment on "Navigation"
Sentiment on "Build Quality"
This focused set of five criteria provides a complete end-to-end pipeline (scraping quantitative data, scraping text data, running an NLP model, and applying a weighted ranking) and creates a solid foundation for adding more criteria in future iterations.


KPIs
KPI 1: Data Pipeline Reliability
Metric: The daily, automated data pipeline (Cloud Scheduler -> Cloud Functions -> BigQuery) must achieve a >95% success rate over a 7-day period.
Definition of Success: A successful run is defined as a run that completes with no errors and loads new data for at least 80% of the vacuums in the curated list into the final BigQuery table.
KPI 2: Data Coverage & Quality
Metric: For the curated list of vacuums, the final BigQuery table must have non-null values for at least 95% of quantitative fields (Price, Carpet Score, etc.) and a successful NLP sentiment extraction for at least 75% of qualitative fields (Battery Life, Navigation, etc.).
KPI 3: Ranking Logic Correctness
Metric: The ranking algorithm must pass a predefined set of "golden set" unit tests with 100% accuracy.
Definition of Success: We will create 3-5 specific test cases. For example:
Test Case A: "Given 'Carpet Deep Clean Score' is the only criterion selected, the top-ranked vacuum must be the one with the highest score in the database."
Test Case B: "Given 'Battery Life' sentiment is the only criterion, the top-ranked vacuum must have the most positive average sentiment score for that aspect."
KPI 4: Application Performance
Metric: The deployed Streamlit application must have a server response time (p95) of less than 2 seconds for generating a ranked list after the user submits their criteria.


Future Work & V2 Roadmap
The V1.0 MVP is intentionally limited to prove the viability of the end-to-end MLOps pipeline. The long-term vision is to create a comprehensive and fully automated product discovery tool. The following features are planned for future versions and will be scoped into a PROJECT_SCOPE_V2.md after the successful deployment of the MVP.

Data Source Expansion:

Integrate additional expert review sites (e.g., CNET, Tom's Guide, Rtings.com).

Expand to other major e-commerce platforms for a wider range of user reviews (e.g., Walmart, Best Buy).

Product Catalog Expansion:

Remove the "curated list" constraint.

Develop a discovery scraper that automatically finds new robot vacuum models as they are released.

Feature & Criteria Expansion:

Incorporate more nuanced criteria from NLP analysis, such as "pet hair performance," "edge cleaning," and "software usability."

Add structured data points like "bin volume," "dimensions," and "warranty period."

Ethical Scalability:

As the number of scraped pages increases, implement a more sophisticated proxy rotation and request throttling strategy to ensure the pipeline remains a "good citizen" and does not overload source servers.


