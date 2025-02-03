import requests
from bs4 import BeautifulSoup
import json
import csv

# Function to fetch all state URLs from the main directory page
def fetch_state_links(base_url):
    print("Fetching state links...")
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all state links
    state_links = soup.find_all('a', class_='view_stateNameLink__qdJ1N') 
    state_urls = []

    for link in state_links:
        state_name = link.get_text(strip=True)
        state_url = 'https://www.target.com' + link['href']
        state_urls.append((state_name, state_url))
    
    return state_urls

# Function to fetch city links for a given state
def fetch_city_links(state_url):
    print()
    print(f"Fetching city links for STATE: {state_url}")
    response = requests.get(state_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all city buttons and city links
    city_links = []
    city_buttons = soup.find_all('div', class_='view_cityName__vSrti')

    # Handle cases where cities have multiple stores (i.e., they have the `data-ids` attribute)
    for button in city_buttons:
        city_name = button.get('data-city')
        data_ids = button.get('data-ids')

        if city_name and data_ids:
            # Split the data-ids into individual store IDs
            store_ids = data_ids.split(',')
            for store_id in store_ids:
                # Construct the URL for each store using city name and store ID
                city_url = f"/sl/{city_name.lower()}/{store_id}"
                
                # Ensure the URL is fully qualified (add 'https://www.target.com' if not already present)
                if not city_url.startswith('https://'):
                    city_url = 'https://www.target.com' + city_url
                
                city_links.append((city_name, city_url))

    # For cities without multiple stores, just grab the links as usual
    regular_city_links = soup.find_all('a', class_='view_cityNameLink__O_Xez')
    for link in regular_city_links:
        city_name = link.get_text(strip=True)
        city_url = 'https://www.target.com' + link['href']
        city_links.append((city_name, city_url))

    return city_links

# Function to fetch store details from a city's store page
def fetch_store_details(city_url):
    print(f"Fetching store details from city page: {city_url}")
    # Make sure the URL is fully qualified
    if not city_url.startswith('https://'):
        city_url = 'https://www.target.com' + city_url

    response = requests.get(city_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the JSON-LD script containing store details
    json_ld_script = soup.find('script', {'data-test': '@store-locator/StoreDetails/JsonLD'})
    store_data = []

    if json_ld_script:
        # Parse the JSON-LD data
        json_data = json.loads(json_ld_script.string)
        
        store_name = json_data.get('name', 'N/A')
        address = json_data['address']
        latitude = json_data['geo']['latitude']
        longitude = json_data['geo']['longitude']
        phone = json_data.get('telephone', 'N/A')
        store_type = ', '.join([dept['name'] for dept in json_data.get('department', [])])

        # Prepare the store details
        store_data = {
            'Store Name': store_name,
            'Address': f"{address['streetAddress']}, {address['addressLocality']}, {address['addressRegion']} {address['postalCode']}",
            'Latitude': latitude,
            'Longitude': longitude,
            'Phone': phone,
            'Store Type': store_type
        }

    return store_data

# Function to save the store data into a CSV file
def save_to_csv(data, filename='target_store_data.csv'):
    print(f"Saving data to CSV file: {filename}")
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['State', 'City', 'Store Name', 'Address', 'Latitude', 'Longitude', 'Phone', 'Store Type']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in data:
            writer.writerow(row)

# Main function to orchestrate the scraping and saving
def main():
    # Base URL for Target store directory
    BASE_URL = 'https://www.target.com/store-locator/store-directory'

    all_store_data = []

    # Step 1: Fetch all state links
    state_links = fetch_state_links(BASE_URL)

    for state_name, state_url in state_links:
        # Step 2: Fetch city links for each state
        city_links = fetch_city_links(state_url)

        for city_name, city_url in city_links:
            # Step 3: Fetch store details for each city
            store_details = fetch_store_details(city_url)

            if store_details:
                # Add state and city information to the store data
                store_details['State'] = state_name
                store_details['City'] = city_name
                all_store_data.append(store_details)

    # Step 4: Save all collected data to a CSV file
    save_to_csv(all_store_data)

if __name__ == '__main__':
    main()
