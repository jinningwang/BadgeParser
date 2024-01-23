import os
import requests
from bs4 import BeautifulSoup
import json

# ISSN to Journal Mapping
issn_to_journal = {
    'issn:1949-3037': 'IEEE Transactions on Sustainable Energy',
    'issn:1949-3061': 'IEEE Transactions on Smart Grid',
    'issn:1937-4208': 'IEEE Transactions on Power Delivery',
    'issn:1558-0679': 'IEEE Transactions on Power Systems',
    'issn:2332-7707': 'IEEE Power and Energy Technology Systems Journal',
    'issn:2367-0983': 'Protection and Control of Modern Power Systems',
    'issn:2634-1581': 'Energy Conversion and Economics',
}

def scrape_google_scholar(profile_url):
    """
    Scrape Google Scholar profile for citation count.

    Parameters
    ----------
    profile_url : str
        URL of the Google Scholar profile.

    Returns
    -------
    str
        The number of citations extracted from the profile.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(profile_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    citations = soup.find_all('td', class_='gsc_rsb_std')[0].text
    return citations

def fetch_orcid_bio(orcid_id):
    """
    Fetch biography information from ORCID.

    Parameters
    ----------
    orcid_id : str
        The ORCID identifier.

    Returns
    -------
    str
        Biography information from ORCID profile.
    """
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/person"
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        orcid_data = response.json()
        biography = orcid_data.get('biography', {}).get('content', '')
        return biography
    else:
        return None

def fetch_orcid_total_review(orcid_id):
    """
    Fetch total number of peer reviews from ORCID.

    Parameters
    ----------
    orcid_id : str
        The ORCID identifier.

    Returns
    -------
    int
        Total number of peer reviews.
    """
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/peer-reviews"
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        orcid_data = response.json()
        total_reviews = 0
        for group in orcid_data.get('group', []):
            for pr_group in group.get('peer-review-group', []):
                total_reviews += len(pr_group.get('peer-review-summary', []))
        return total_reviews
    else:
        return None

def fetch_orcid_review_data(orcid_id):
    """
    Fetch peer review data from ORCID and map ISSNs to journal names.

    Parameters
    ----------
    orcid_id : str
        The ORCID identifier.

    Returns
    -------
    dict
        A dictionary with journal names as keys and review counts as values.
    """
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/peer-reviews"
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    review_counts = {}  # Dictionary to store review counts per journal
    if response.status_code == 200:
        orcid_data = response.json()
        for group in orcid_data.get('group', []):
            for pr_group in group.get('peer-review-group', []):
                for review in pr_group.get('peer-review-summary', []):
                    issn = review.get('review-group-id', 'Unknown')
                    journal_name = issn_to_journal.get(issn, 'Unknown Journal')
                    review_counts[journal_name] = review_counts.get(journal_name, 0) + 1
    return review_counts

def fetch_orcid_publication_data(orcid_id):
    """
    Fetch publication data from an ORCID profile. (Placeholder function)

    Parameters
    ----------
    orcid_id : str
        ORCID identifier

    Returns
    -------
    dict
        A dictionary representing publication data (to be implemented)
    """
    publication_counts = {}  # Example placeholder
    return publication_counts

def write_to_json(data, filename):
    """
    Write data to a JSON file.

    Parameters
    ----------
    data : dict
        Data to be written to the file
    filename : str
        Name of the file to be written
    """
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)

def main():
    """
    Main execution function for the script.
    """
    gs_profile_url = 'https://scholar.google.com/citations?user=Wr7nQZAAAAAJ&hl=en&oi=ao'
    orcid_id = '0000-0001-9302-3364'

    gs_citations = scrape_google_scholar(gs_profile_url)
    orcid_bio = fetch_orcid_bio(orcid_id)
    orcid_total_review = fetch_orcid_total_review(orcid_id)
    review_data = fetch_orcid_review_data(orcid_id)
    publication_data = fetch_orcid_publication_data(orcid_id)

    scholar_data = {
        'gscitations': gs_citations,
        'orcidtotalreview': orcid_total_review,
        'orcidbio': orcid_bio
    }

    write_to_json(scholar_data, 'data_scholar.json')
    write_to_json(review_data, 'data_review.json')
    write_to_json(publication_data, 'data_pub.json')

if __name__ == "__main__":
    main()
