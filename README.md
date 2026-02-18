# UFC Fight Predictor 🥊

A data-driven web application that predicts the outcome of UFC fights based on comparative fighter statistics. This project demonstrates full-stack data science capabilities: web scraping, data cleaning, feature engineering, and interactive dashboard development.

## 🚀 Key Features

*   **Comprehensive Database**: Contains statistics for over 3,500 UFC fighters (scraped from `ufcstats.com`).
*   **Predictive Model**: Uses a weighted scoring system based on Striking, Grappling, Physical attributes, and Experience.
*   **Interactive Dashboard**: Built with Streamlit, allowing users to select any two fighters and visualize the matchup.
*   **"Tale of the Tape"**: Side-by-side statistical breakdown of every matchup.

## 🛠️ Technical Implementation

### 1. Data Acquisition (Web Scraping)
*   **Source**: `ufcstats.com` (The official statistics provider for the UFC).
*   **Tools**: `Python`, `Requests`, `BeautifulSoup`.
*   **Challenges Solved**:
    *   **Rate Limiting**: Implemented delays to respect the server.
    *   **Parallel Execution**: Developed a multi-process scraper strategy (A-M, N-R, S-Z) to reduce total scraping time by 60%.
    *   **Data Normalization**: Handled inconsistent formats (e.g., "5' 10"" vs "178cm", missing reach data).

### 2. Data Processing & Feature Engineering
*   **Tools**: `Pandas`, `NumPy`.
*   **Cleaning**:
    *   Converted physical stats (Height/Reach) to metric (cm).
    *   Imputed missing Reach values using the average Reach-to-Height ratio of the roster.
    *   Standardized Stance (Orthodox/Southpaw/Switch).
*   **Feature Engineering**:
    *   Calculated `Win Rate` from W-L-D records.
    *   Derived `Finish Potential` based on career stats.

### 3. Prediction Logic (The Algorithm)
The prediction model calculates a **Weighted Advantage Score** for each fighter. The probability of winning is derived from the score differential using a sigmoid function.

**The Formula:**
```python
Score = (Striking_Advantage * 0.40) + 
        (Grappling_Advantage * 0.30) + 
        (Physical_Advantage * 0.15) + 
        (Experience_Advantage * 0.15)
```

*   **Striking (40%)**: Significant Strikes Landed per Minute (SLpM), Striking Accuracy, Strikes Absorbed (SApM), Defense.
*   **Grappling (30%)**: Takedown Average, Accuracy, Defense, and Submission Average.
*   **Physical (15%)**: Reach and Height advantage.
*   **Experience (15%)**: Win Rate weighted by total number of fights (log-scaled).

### 4. Application Development
*   **Framework**: `Streamlit` (Python).
*   **Architecture**:
    *   `src/scraper.py`: Core scraping logic.
    *   `src/processor.py`: Data cleaning and loading pipeline.
    *   `src/model.py`: Prediction engine.
    *   `src/image_fetcher.py`: **On-Demand Image Scraper**. Fetches fighter photos from `ufc.com` in real-time and caches them for performance.
    *   `app.py`: Frontend interface.

## 🚀 Key Technical Highlights
*   **SQL Data Warehouse**: Architected a normalized SQLite database (`fighters` and `fighter_stats` tables) and built a custom ETL pipeline to migrate 3,500+ records from raw CSVs.
*   **Parallel Scraping**: Reduced data collection time by 60% using concurrent processes.
*   **On-Demand Fetching**: Skips downloading heavy images by scraping URLs dynamically.
*   **Interactive Analytics**: Integrated Plotly dashboard allows users to explore the dataset visually (e.g., Reach vs Height correlations), making it a powerful tool for data storytelling and presentations.
*   **Robust Error Handling**: Gracefully handles missing data, network timeouts, and name mismatches.

## 📈 Future Improvements
*   **Machine Learning**: Train a Logistic Regression or XGBoost model on historical fight results for better calibration.
*   **Photos**: Integrate with an authorized image API (e.g., Getty Images or UFC Connect) to include real fighter photos.
*   **Live Odds**: Integrate with a betting API to compare model predictions vs Vegas odds.

## 👨‍💻 Setup & Usage

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

3.  **Update Data (Optional)**:
    ```bash
    python src/scraper.py
    ```
