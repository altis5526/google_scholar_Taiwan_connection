from serpapi import GoogleSearch
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from argparse import ArgumentParser


def find_taiwan_connections(author_id, author_name=None):
    # Configure API parameters
    params = {
        "api_key": os.getenv("SERPAPI_KEY"),  # Register at serpapi.com
        "engine": "google_scholar_author",
        "author_id": author_id,  # The professor's Google Scholar ID
        "view_op": "list_colleagues",
        "hl": "en"
    }
    
    # Fetch author data
    search = GoogleSearch(params)
    results = search.get_dict()
    
    # Extract co-authors information
    co_authors = results.get("co_authors", [])
    taiwan_institutions = [
        "national taiwan university", "national cheng kung university", 
        "national tsing hua university", "national chiao tung university", 
        "national yang ming chiao tung university",
        "academia sinica", "taipei", "kaohsiung", "taichung", "tainan", "taiwan"
    ]
    
    # Filter co-authors with Taiwan affiliations
    taiwan_connections = []
    for co_author in co_authors:
        affiliation = co_author.get("affiliations", "").lower()
        for institution in taiwan_institutions:
            if institution in affiliation:
                taiwan_connections.append({
                    "name": co_author.get("name"),
                    "affiliation": co_author.get("affiliations"),
                    "author_id": co_author.get("author_id"),
                    "email": co_author.get("email"),
                    "connected_author": author_name,
                })
    
    return taiwan_connections


def get_scholar_id_by_name(professor_name):
    # Format the name for URL
    query = professor_name.replace(' ', '+')
    url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Look for the first result (most relevant)
        author_link = soup.select_one('div.gs_ai_t h3 a')
        
        if author_link:
            profile_url = author_link['href']
            # Extract ID from URL format: /citations?user=XXXX&hl=en
            scholar_id = profile_url.split('user=')[1].split('&')[0]
            return scholar_id
    
    return None


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    parser = ArgumentParser()
    parser.add_argument("--author_name", type=str, help="Name of the author to search for")
    args = parser.parse_args()
    author_name =  args.author_name
    scholar_id = get_scholar_id_by_name(author_name)
    # Example usage
    connections = find_taiwan_connections(scholar_id, author_name)  # Replace with professor's ID
    print(f"Found {len(connections)} connections in Taiwan")

    # Export results to CSV
    if connections:
        df = pd.DataFrame(connections)
        df.to_csv("taiwan_connections.csv", mode="a", header=False, index=False)
