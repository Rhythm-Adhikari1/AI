# GNews Data Pipeline

A production-ready data pipeline that fetches news headlines from the GNews API, prevents duplicates, and answers 8 analytical questions.

## Overview

This pipeline:
- Fetches headlines from 5 countries (Nepal, India, USA, UK, Australia)
- Saves data to CSV with deduplication (MD5 hashing)
- Answers 8 analytical questions by reading from CSV
- Filters headlines with titles longer than 6 words
- Handles missing data with "N/A" placeholders

## Quick Start

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Get API key from https://gnews.io/
# Add to .env file:
GNEWS_API_KEY=your_key_from_gnews
```

### Run Pipeline

```bash
python run_pipeline.py
```

This fetches headlines and answers all 8 questions.

## Architecture

| Component | Purpose |
|-----------|---------|
| gnews_pipeline.py | Fetch from API, deduplicate, save to CSV |
| analyze_headlines.py | Read CSV, analyze, answer 8 questions |
| run_pipeline.py | Orchestrate both scripts (entry point) |
| headlines.csv | Main database (auto-created) |
| headlines_long_titles.csv | Filtered output, >6 words (auto-created) |

## Questions Answered

1. Which country published the most headlines?
2. Average word count per headline by country?
3. Any headlines appearing in multiple countries?
4. Most prolific news source across all countries?
5. Percentage of headlines from last 6 hours vs older?
6. How is duplicate prevention implemented?
7. How many headlines have titles > 6 words?
8. Which country has longest/shortest average headline?

## CSV Format

### Columns (all lowercase, no spaces)

```
country, title, description, url, image, source, 
published_at, article_content, headline_hash
```

- All empty fields filled with "N/A"
- No duplicate rows (hash-based deduplication)
- RFC 4180 compliant

## Duplicate Prevention

**Method:** MD5 hash of (title + source)

**Process:**
1. Generate hash for each headline
2. Load existing hashes from CSV
3. Check if hash exists before insert
4. Skip duplicates, add only new headlines

**Result:** Running twice adds only new headlines, never duplicates

Example:
- Run 1: 50 headlines → CSV has 50 rows
- Run 2: 50 fetched (40 same, 10 new) → CSV has 60 rows (only 10 new added)

## Usage

### Individual Steps

```bash
# Fetch headlines only
python gnews_pipeline.py

# Analyze existing data
python analyze_headlines.py

# Run complete pipeline
python run_pipeline.py
```

### Validation

```bash
# Check CSV structure
head -1 headlines.csv

# Count total rows
wc -l headlines.csv

# Verify no duplicates
cut -d',' -f9 headlines.csv | sort | uniq -d
# (should return nothing)
```

## Output Example

```
Checking prerequisites...
[OK] API key configured
[OK] requests library installed

Fetching headlines for Nepal...
  [OK] Found 10 headlines for Nepal
Fetching headlines for India...
  [OK] Found 10 headlines for India
...
[OK] Saved 49 new headlines to headlines.csv

Q1: Most headlines by country?
India published the most headlines with 10 headlines

Q2: Average words per headline by country?
India: 9.50 words
Nepal: 9.40 words
...
```

## Configuration

### Required Files

- .env - Add API key: `GNEWS_API_KEY=your_key`
- requirements.txt - Dependencies: requests, python-dotenv

### API Information

- Source: GNews (https://gnews.io/)
- Free tier: 100 requests per day
- Endpoint: /top-headlines
- Docs: https://docs.gnews.io/

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not set" | Add GNEWS_API_KEY to .env |
| "requests not found" | Run: pip install requests |
| "No headlines fetched" | Verify API key is valid |
| "Empty CSV" | Check network connection |
| "Duplicates in CSV" | Verify headline_hash column has values |

## Performance

| Metric | Value |
|--------|-------|
| API calls per run | 5 |
| Headlines per run | 40-50 |
| Runtime | 10-30 seconds |
| CSV file size | 50-100 KB per run |

## Implementation Details

- Language: Python 3.7+
- Storage: CSV (no database required)
- Deduplication: O(1) hash lookup
- Data validation: All fields populated
- Error handling: Graceful with clear messages
