import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urlparse, parse_qs

# Function to get all seat URLs from the main page
def get_seat_urls(main_url):
    try:
        response = requests.get(main_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assuming links to seats are found in <a> tags with a specific pattern
        seat_links = []
        for link in soup.find_all('a', href=True):
            if "division_results.php" in link['href']:  # Update this condition based on the site structure
                seat_links.append(link['href'])

        # Full URLs if needed
        seat_links = [f"https://results.elections.gov.lk/{link}" for link in seat_links]
        return seat_links
    except Exception as e:
        print(f"Error fetching seat URLs from the main page: {e}")
        return []

# Function to extract district and seat names from the URL
def extract_district_and_seat(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    district = query_params.get('district', [''])[0]  # Get district name
    seat = query_params.get('pd_division', [''])[0]  # Get seat name
    return district, seat

# Function to scrape data from each seat's page
def scrape_seat_data(seat_url):
    start_time = time.time()
    try:
        response = requests.get(seat_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract district and seat from URL
        district, seat = extract_district_and_seat(seat_url)

        # Extracting the release date with error handling
        release_date_element = soup.find('p', class_='card-subtitle')

        if not release_date_element:
            print(f"Error: Required elements not found on {seat_url}")
            return []  # Return empty list if elements are missing

        release_date = release_date_element.text.strip()

        # Initialize a list to collect candidates' data
        combined_data = []

        # Scrape candidate results from the first table with error handling
        candidate_table = soup.select('table.select-table')[0] if len(soup.select('table.select-table')) > 0 else None
        if candidate_table:
            rows = candidate_table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:  # Ensure there are enough columns
                    combined_data.append({
                        'District': district,  # Add district column
                        'Seat': seat,  # Add seat column
                        'Release_date': release_date,
                        'Candidate_name': cols[0].text.strip(),
                        'Party_abbreviation': cols[1].text.strip(),
                        'Votes_received': int(cols[2].text.strip().replace(',', '')),
                        'Percentage': float(cols[3].text.strip().replace('%', ''))
                    })

        # Define a mapping for the overall data fields
        overall_field_mapping = {
            'Valid Votes': 'Valid_votes_in_seat',
            'Rejected Votes': 'Rejected_votes_in_seat',
            'Total Polled': 'Total_polled_in_seat',  # Add this line
            'Total Electors': 'Total_electors_in_seat'  # Add this line
        }

        # Scrape the second table for overall results
        overall_data = {
            'District': district,  # Add district column
            'Seat': seat,  # Add seat column
            'Release_date': release_date
        }

        overall_table = soup.select('table.select-table')[1] if len(soup.select('table.select-table')) > 1 else None
        if overall_table:
            print(f"Found second table on {seat_url}")  # Confirm the table is found
            overall_rows = overall_table.find_all('tr')
            print(f"Overall table rows found: {len(overall_rows)}")  # Check number of rows
            for row in overall_rows:
                cols = row.find_all('td')
                print(f"Row columns found: {len(cols)} | Content: {[col.text for col in cols]}")  # Print the columns found
                if len(cols) >= 2:  # Adjusted condition to handle three columns, taking only the first two
                    key = cols[0].text.strip()
                    value = cols[1].text.strip().replace(',', '')

                    # Attempt to get the overall field value and handle possible conversion issues
                    try:
                        if key in overall_field_mapping:
                            overall_data[overall_field_mapping[key]] = int(value.replace(',', '')) if value.isdigit() else 0
                        else:
                            print(f"Warning: Key '{key}' not found in overall_field_mapping.")
                    except ValueError:
                        print(f"Warning: Could not convert value '{value}' to an integer.")

        else:
            print(f"No second table found on {seat_url}")

        # Combine overall data into each candidate's data
        for data in combined_data:
            data.update(overall_data)

        end_time = time.time()
        print(f"Scraping successful for {seat_url} | Time taken: {end_time - start_time:.2f} seconds")
        return combined_data
    except Exception as e:
        end_time = time.time()
        print(f"Failed to scrape {seat_url}: {e} | Time taken: {end_time - start_time:.2f} seconds")
        return []  # Return empty list in case of errors

# Main script to iterate through all pages and collect data into a single dataset
def main(test_mode=False, test_limit=5):
    main_url = 'https://results.elections.gov.lk'  # Update with the main results page URL
    seat_urls = get_seat_urls(main_url)

    # If in test mode, limit the number of URLs processed
    if test_mode:
        seat_urls = seat_urls[:test_limit]

    # List to collect all combined data
    all_combined_data = []

    # Scrape data for each seat
    for seat_url in seat_urls:
        combined_data = scrape_seat_data(seat_url)
        all_combined_data.extend(combined_data)  # Append combined data for each seat
        time.sleep(2)  # Respectful delay to avoid overloading the server

    # Convert combined data into a DataFrame and save to CSV
    if all_combined_data:
        df_combined = pd.DataFrame(all_combined_data)
        df_combined.to_csv('out/sl_2024_presidential_election_results_dataset.csv', index=False)
        print("Combined data saved successfully.")
    else:
        print("No combined data collected.")

    print("Data scraping and saving completed!")

# Run the main function
if __name__ == "__main__":
    main(test_mode=False)  # Set the limit as needed for testing
