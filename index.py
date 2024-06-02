from curl_cffi import requests
from bs4 import BeautifulSoup
import csv

filename = 'realestate.csv'

def make_csv(data):
    # Open the CSV file in append mode
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='#', quoting=csv.QUOTE_MINIMAL)
        
        # If the file is empty, write the header row
        if csvfile.tell() == 0:
            csvwriter.writerow(['Address', 'Link', 'Price', 'Bedrooms', 'Bathrooms', 'Parking Spaces', 'Property Type', 'Indicative Price Link', 'Property Size'])
        
        # Write each row of data to the CSV file
        for row in data:
            csvwriter.writerow(row)

session = requests.Session()

def scrap_details(properties):
    data = []
    for prop in properties:
        # Extract the address
        address = prop.select_one('.residential-card__address-heading .details-link span').text.strip()
        
        # Extract the price
        price = prop.select_one('.residential-card__price span')
        price = price.text.strip() if price else 'N/A'
        
        # Extract the link
        link = prop.select_one('.residential-card__address-heading .details-link')['href']
        
        # Extract the number of bedrooms, bathrooms, and parking spaces
        details = prop.select('.View__PropertyDetail-sc-11ysrk6-0')
        bedrooms = details[0].text.strip() if details and len(details) > 0 else 'N/A'
        bathrooms = details[1].text.strip() if details and len(details) > 1 else 'N/A'
        parking_spaces = details[2].text.strip() if details and len(details) > 2 else 'N/A'
        
        # Extract the property type
        property_type = prop.select_one('.residential-card__property-type').text.strip()
        
        # Extract the indicative price link
        price_link_tag = prop.select_one('.price-guide-fallback a')
        price_link = price_link_tag['href'] if price_link_tag else 'N/A'
        
        # Extract the property size
        property_size = soup.select_one('.property-size').text.strip()
        
        # Append the data to the list
        data.append([address, link, price, bedrooms, bathrooms, parking_spaces, property_type, price_link, property_size])
    
    # Call the make_csv function to write the data to the CSV file
    make_csv(data)

page = 1
total_page = None

# Get the location name from the user
location_name = input('Enter the location name: ')

# If the location name is empty, exit the program
if location_name == '':
    exit()

# Construct the query URL to get location suggestions
query_url = f"https://suggest.realestate.com.au/consumer-suggest/suggestions?max=7&type=suburb%2Cregion%2Cprecinct%2Cstate%2Cpostcode&src=homepage-web&query={location_name}"
query_response = session.get(query_url)
query_data = query_response.json()
options = []
query_data = query_data['_embedded']['suggestions']

# Display the location options to the user
for i in range(len(query_data)):
    print(f"{i} " + query_data[i]['display']['text'])
    options.append(query_data[i]['display']['text'])

# Get the user's choice for the location
choice = int(input('Enter the choice: '))
location = options[choice]
location_name = "+".join([x.lower() for x in location.split(' ')])

while(1):
    # Construct the URL for the property listings
    url = f'https://www.realestate.com.au/buy/in-{location_name}/list-{page}?activeSort=relevance'
    print(url)
    response = session.options(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    properties = soup.find_all('div', class_='residential-card__content')
    
    # Scrape the details of each property
    scrap_details(properties)
    
    # Increment the page number
    page += 1
    
    # Get the total number of pages
    pageinations = soup.find('div', class_='styles__PaginationNumbers-sc-1ciwyuo-5')
    if total_page is None:
        total_page = int(pageinations.find_all('a')[-1].text)
    
    # Break the loop if all pages have been scraped
    if page > total_page:
        break
