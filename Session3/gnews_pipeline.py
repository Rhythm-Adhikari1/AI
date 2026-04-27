"""
GNews API Data Pipeline
Fetches headlines for 5 countries, saves to CSV, and prevents duplicates.
"""

import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Set
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GNEWS_API_KEY = os.getenv('GNEWS_API_KEY', '')
GNEWS_API_URL = 'https://gnews.io/api/v4'
COUNTRIES = ['Nepal', 'India', 'USA', 'UK', 'Australia']
COUNTRY_CODES = {
    'Nepal': 'np',
    'India': 'in',
    'USA': 'us',
    'UK': 'gb',
    'Australia': 'au'
}
OUTPUT_CSV = 'headlines.csv'
CSV_COLUMNS = [
    'country', 'title', 'description', 'url', 'image', 'source', 
    'published_at', 'article_content', 'headline_hash'
]


def get_existing_headlines_hashes() -> Set[str]:
    """
    Get all existing headline hashes from CSV to prevent duplicates.
    """
    hashes = set()
    if os.path.exists(OUTPUT_CSV):
        try:
            with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('headline_hash'):
                        hashes.add(row['headline_hash'])
        except Exception as e:
            print(f"Warning: Could not read existing CSV: {e}")
    return hashes


def generate_headline_hash(title: str, source: str) -> str:
    """
    Generate a unique hash for a headline (title + source combination).
    This helps identify duplicate headlines across runs.
    """
    unique_id = f"{title}|{source}".lower().strip()
    return hashlib.md5(unique_id.encode()).hexdigest()


def fetch_headlines(country: str, country_code: str) -> List[Dict]:
    """
    Fetch headlines from GNews API for a specific country.
    """
    print(f"Fetching headlines for {country}...")
    
    params = {
        'category': 'general',  # Required parameter
        'country': country_code,
        'lang': 'en',
        'max': 10,  # Free tier limit per request
        'apikey': GNEWS_API_KEY
    }
    
    try:
        response = requests.get(f'{GNEWS_API_URL}/top-headlines', params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'articles' in data:
            print(f"  [OK] Found {len(data['articles'])} headlines for {country}")
            return data['articles']
        else:
            print(f"  [NONE] No articles found for {country}")
            return []
    except Exception as e:
        print(f"  [ERROR] Error fetching {country}: {e}")
        return []


def process_articles(articles: List[Dict], country: str, existing_hashes: Set[str]) -> List[Dict]:
    """
    Process articles, creating clean rows and filtering duplicates.
    """
    processed = []
    
    for article in articles:
        # Create a unique hash for this headline
        title = article.get('title', 'N/A').strip()
        source = article.get('source', {}).get('name', 'N/A') if isinstance(article.get('source'), dict) else article.get('source', 'N/A')
        source = str(source).strip() if source else 'N/A'
        
        headline_hash = generate_headline_hash(title, source)
        
        # Skip if this headline already exists in the CSV
        if headline_hash in existing_hashes:
            print(f"    - Skipping duplicate: {title[:50]}...")
            continue
        
        row = {
            'country': country,
            'title': title if title else 'N/A',
            'description': article.get('description', 'N/A') or 'N/A',
            'url': article.get('url', 'N/A') or 'N/A',
            'image': article.get('image', 'N/A') or 'N/A',
            'source': source,
            'published_at': article.get('publishedAt', 'N/A') or 'N/A',
            'article_content': article.get('content', 'N/A') or 'N/A',
            'headline_hash': headline_hash
        }
        processed.append(row)
        existing_hashes.add(headline_hash)
    
    return processed


def save_to_csv(headlines: List[Dict]):
    """
    Save headlines to CSV, appending if file exists, creating if not.
    """
    file_exists = os.path.exists(OUTPUT_CSV)
    
    try:
        with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            
            # Write header only if file doesn't exist
            if not file_exists:
                writer.writeheader()
            
            writer.writerows(headlines)
        
        print(f"\n[OK] Saved {len(headlines)} new headlines to {OUTPUT_CSV}")
    except Exception as e:
        print(f"[ERROR] Error saving to CSV: {e}")


def main():
    """
    Main pipeline: fetch headlines for all countries and save to CSV.
    """
    print("GNews Data Pipeline - Starting")
    
    
    if not GNEWS_API_KEY:
        print("[ERROR] GNEWS_API_KEY not set in environment variables")
        print("  Add GNEWS_API_KEY to .env file")
        return False
    
    # Get existing hashes to prevent duplicates
    existing_hashes = get_existing_headlines_hashes()
    print(f"Found {len(existing_hashes)} existing unique headlines in CSV\n")
    
    all_headlines = []
    
    # Fetch headlines for each country
    for country in COUNTRIES:
        country_code = COUNTRY_CODES[country]
        articles = fetch_headlines(country, country_code)
        
        if articles:
            processed = process_articles(articles, country, existing_hashes)
            all_headlines.extend(processed)
    
    # Save new headlines to CSV
    if all_headlines:
        save_to_csv(all_headlines)
    else:
        print("\n[NONE] No new headlines to save")
    
    
    print("Pipeline Complete!")
    
    return True


if __name__ == "__main__":
    main()
