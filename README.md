# Web Scraping Project

## Overview
This project is a web scraping application that extracts election results from the official election results website of Sri Lanka. Using Python with libraries like Requests, Beautiful Soup, and Pandas, this project gathers and processes data efficiently to provide insights into election results.

## Features
- Scrapes individual seat results from the main results page.
- Extracts candidate names, party abbreviations, votes received, and vote percentages.
- Collects overall election results for each seat.
- Saves the combined data into a CSV file for easy analysis.

## Code Explanation
- **`main.py`**: The main script where the scraping logic is implemented.
  - **`get_seat_urls(main_url)`**: Fetches all seat URLs from the main results page.
  - **`extract_district_and_seat(url)`**: Extracts the district and seat names from the seat URL.
  - **`scrape_seat_data(seat_url)`**: Scrapes data from an individual seat's page and combines it with overall results.
  - **`main(test_mode=False, test_limit=5)`**: Main function to iterate through all seat pages and collect data.

## Data Output
The scraped data will be saved in `out/combined_results.csv` in the following format:
- **District**
- **Seat**
- **Release Date**
- **Candidate Name**
- **Party Abbreviation**
- **Votes Received**
- **Percentage**

## Project Setup Guide
1. **Clone the repository**:
   ```bash
   `git clone https://github.com/yourusername/your-repo-name.git`

Navigate to the project directory:
`cd your-repo-name`

Create and activate a virtual environment:
`python -m venv venv`
# On Linux/mac `source venv/bin/activate`
# On Windows use `venv\Scripts\activate`

Install the required packages:
`pip install -r requirements.txt`

Run the main script:
`python main.py`

This will start the scraping process and save the results to out/combined_results.csv.


## Testing Mode
You can run the scraper in test mode to limit the number of URLs processed:
`main(test_mode=True, test_limit=5)`

## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request. Feel free to report issues or suggest improvements.
