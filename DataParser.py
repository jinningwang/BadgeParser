import requests
from bs4 import BeautifulSoup
import json
import logging

# ISSN to Journal Mapping
issn_to_journal = {
    'issn:1949-3037': 'TSTE',
    'issn:1949-3061': 'TSG',
    'issn:1937-4208': 'TRWRD',
    'issn:1558-0679': 'TPWRS',
    'issn:2332-7707': 'OAJPE',
    'issn:2367-0983': 'PCMP',
    'issn:2634-1581': 'EnergyConversionAndEconomics',
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
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        citations = soup.find_all('td', class_='gsc_rsb_std')[0].text
        return citations
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while scraping Google Scholar: {e}")
        return None


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
    try:
        url = f"https://pub.orcid.org/v3.0/{orcid_id}/person"
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        orcid_data = response.json()
        biography = orcid_data.get('biography', {}).get('content', '')
        return biography
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while fetching ORCID biography: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response from ORCID: {e}")
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
                    review_counts[journal_name] = review_counts.get(
                        journal_name, 0) + 1
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


def generate_citation_badge(citations, logo=None, link=None):
    """
    Generate a badge for the number of citations with an optional link.

    Parameters
    ----------
    citations : str
        The number of citations to display on the badge.
    logo : str, optional
        Logo name (e.g., "googlescholar").
    link : str, optional
        URL to link when the badge is clicked.

    Returns
    -------
    str
        The Markdown code for the badge.
    """
    label = "G Scholar Citations"  # Label without URL encoding
    message = citations
    color = "blue"  # You can choose a color for the badge

    # Construct the Shields.io URL manually with the logo parameter
    if logo:
        badge_url = f"https://img.shields.io/badge/{label.replace(' ', '%20')}-{message}-{color}.svg?logo={logo}"
    else:
        badge_url = f"https://img.shields.io/badge/{label.replace(' ', '%20')}-{message}-{color}.svg"

    # Add the link parameter if provided
    if link:
        badge_url += f"&link={link}"

    # Generate Markdown code for the badge
    badge_markdown = f"![{label}]({badge_url})"

    return badge_markdown


def generate_review_badge(journal_name, review_count, color="blue", logo=None, link=None):
    """
    Generate a badge for review information with an optional link.

    Parameters
    ----------
    journal_name : str
        The journal name to display on the badge.
    review_count : int
        The number of reviews to display on the badge.
    color : str, optional
        Badge color (default is "blue").
    logo : str, optional
        Logo name (e.g., "googlescholar").
    link : str, optional
        URL to link when the badge is clicked.

    Returns
    -------
    str
        The Markdown code for the badge.
    """
    label = journal_name
    message = str(review_count)

    # Construct the Shields.io URL manually with the logo parameter
    if logo:
        badge_url = f"https://img.shields.io/badge/{label.replace(' ', '%20')}-{message}-{color}.svg?logo={logo}"
    else:
        badge_url = f"https://img.shields.io/badge/{label.replace(' ', '%20')}-{message}-{color}.svg"

    # Add the link parameter if provided
    if link:
        badge_url += f"&link={link}"

    # Generate Markdown code for the badge
    badge_markdown = f"![{label}]({badge_url})"

    return badge_markdown



def generate_and_write_badges(citations,
                              review_data,):
    """
    Generate and print the Google Scholar citation badge.

    Parameters
    ----------
    citations : str
        The number of citations to display on the citation badge.
    review_data : dict
        A dictionary with journal names as keys and review counts as values.
    """
    gscholar_link = "https://scholar.google.com/citations?user=Wr7nQZAAAAAJ&hl=en&oi=ao"
    gscholar_badge_markdown = generate_citation_badge(citations,
                                             logo="googlescholar",
                                             link=gscholar_link)
    logging.info(gscholar_badge_markdown)

    # Generate and print review badges for each journal
    for journal_name, review_count in review_data.items():
        review_badge_markdown = generate_review_badge(journal_name, review_count,
                                                      color="blue", logo="None", link=None)
        logging.info(review_badge_markdown)

    # BadgeParser
    readme_header = "# BadgeParser\nCreate customized badges.\n"

    # Write the badge Markdown code to Badge.md
    with open("README.md", "w") as badge_file:
        badge_file.write(readme_header)

        badge_file.write("## Scholar\n")
        badge_file.write(gscholar_badge_markdown)
        badge_file.write("\n")

        badge_file.write("## Peer Review\n")
        for journal_name, review_count in review_data.items():
            review_badge_markdown = generate_review_badge(journal_name, review_count, color="blue", logo=None, link=None)
            badge_file.write(f"{review_badge_markdown}  ")

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

    # Update the README.md file with the Google Scholar citation badge
    generate_and_write_badges(gs_citations, review_data)

    scholar_data = {
        'gscite': gs_citations,
        'orcidtotalreview': orcid_total_review,
        'orcidbio': orcid_bio
    }

    write_to_json(scholar_data, 'data_scholar.json')
    write_to_json(review_data, 'data_review.json')
    write_to_json(publication_data, 'data_pub.json')


if __name__ == "__main__":
    main()
