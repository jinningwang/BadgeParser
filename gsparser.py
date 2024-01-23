import requests
from bs4 import BeautifulSoup
import json


def scrape_google_scholar(profile_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(profile_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the element that contains citations. This might change depending on Google Scholar's layout
    # Usually, it's under a div with class 'gsc_rsb_std'
    citations = soup.find_all('td', class_='gsc_rsb_std')[0].text

    return citations


# Replace this URL with the URL of your Google Scholar profile
profile_url = 'https://scholar.google.com/citations?user=Wr7nQZAAAAAJ&hl=en&oi=ao'
citations = scrape_google_scholar(profile_url)

# Assuming 'citations' variable holds your scraped data
data = {'citations': citations}

# Write data to a JSON file
with open('gscholar_data.json', 'w') as json_file:
    json.dump(data, json_file)
