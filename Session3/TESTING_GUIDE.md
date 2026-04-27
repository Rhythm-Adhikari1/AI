# Testing Guide

## Validation

### Check CSV Structure

```bash
# Verify column names (9 columns expected)
head -1 headlines.csv

# Count total rows
wc -l headlines.csv

# Check for empty cells (should be 0)
grep ',,\|,$' headlines.csv | wc -l
```

### Verify No Duplicates

```bash
# Check headline_hash uniqueness (should return nothing)
cut -d',' -f9 headlines.csv | sort | uniq -d

# Count unique hashes
cut -d',' -f9 headlines.csv | sort -u | wc -l

# Compare to total rows (should be same number)
wc -l headlines.csv
```

## Duplicate Prevention Test

### Run Twice and Verify

```bash
# First run
python run_pipeline.py

# Wait a moment
sleep 30

# Second run
python run_pipeline.py
```

**Expected behavior:**
- First run: Saves ~40-50 headlines
- Second run: Skips duplicates, adds only new headlines
- Result: No duplicate rows in CSV

### Manual Duplicate Check

```python
import csv

hashes = set()
duplicates = 0
total = 0

with open('headlines.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += 1
        hash_val = row['headline_hash']
        if hash_val in hashes:
            duplicates += 1
        hashes.add(hash_val)

print(f"Total rows: {total}")
print(f"Unique hashes: {len(hashes)}")
print(f"Duplicates found: {duplicates}")
```

Expected output: `Duplicates found: 0`

## Data Validation

### Verify All Fields Populated

```bash
# Check for empty values (should be N/A only)
grep -v '^country' headlines.csv | grep -E '^[^,]*$|,[^,]*,[^,]*$' | head
```

### Check Data Types

```python
import csv

with open('headlines.csv', 'r') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 5:  # Check first 5 rows
            break
        
        # Verify required fields
        assert row['country'] in ['Nepal', 'India', 'USA', 'UK', 'Australia']
        assert len(row['title']) > 0
        assert row['title'] != 'N/A'
        assert len(row['headline_hash']) == 32  # MD5 is 32 chars
        print(f"Row {i}: OK")
```

## Analysis Verification

### Run Analysis and Validate Output

```bash
python analyze_headlines.py
```

Verify output contains:
- Q1: Country with most headlines
- Q2: Average words per country
- Q3: Multi-country headlines
- Q4: Top news source
- Q5: 6-hour time split
- Q6: Duplicate prevention explanation
- Q7: Long headlines count
- Q8: Country rankings

### Check Filtered Output

```bash
# Verify filtered file exists and has correct data
head -1 headlines_long_titles.csv

# Count rows in filtered file
wc -l headlines_long_titles.csv

# Verify all titles have > 6 words
python3 << 'EOF'
import csv
with open('headlines_long_titles.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        words = len(row['title'].split())
        assert words > 6, f"Title with {words} words found"
print("All titles have > 6 words: OK")
EOF
```

## Performance Testing

### Measure Execution Time

```bash
time python run_pipeline.py
```

Expected: 10-30 seconds total

### Check File Size

```bash
# Size of CSV after each run
ls -lh headlines.csv

# Should grow ~50-100 KB per run
```

## Error Handling

### Test Missing API Key

```bash
# Comment out API key in .env
# GNEWS_API_KEY=

python run_pipeline.py
# Should display: [ERROR] GNEWS_API_KEY not set
```

### Test Invalid API Key

```bash
# Edit .env with invalid key
GNEWS_API_KEY=invalid_key_12345

python run_pipeline.py
# Should handle API errors gracefully
```

### Test Network Issues

```bash
# Disable network temporarily and run
python gnews_pipeline.py
# Should handle timeout/connection errors
```

## CSV Compliance

### RFC 4180 Validation

```python
import csv
import sys

try:
    with open('headlines.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for row in reader:
            row_count += 1
            # Verify all columns present
            assert 'country' in row
            assert 'title' in row
            assert 'headline_hash' in row
    
    print(f"CSV valid: {row_count} rows processed successfully")
except Exception as e:
    print(f"CSV validation failed: {e}")
    sys.exit(1)
```

## Integration Test

### Complete Pipeline Test

```bash
# Clean start
rm -f headlines.csv headlines_long_titles.csv

# Run pipeline
python run_pipeline.py

# Verify both CSVs created
test -f headlines.csv && echo "headlines.csv created"
test -f headlines_long_titles.csv && echo "headlines_long_titles.csv created"

# Verify data in both
wc -l headlines.csv
wc -l headlines_long_titles.csv

# Second run
python run_pipeline.py

# Verify no duplicates
cut -d',' -f9 headlines.csv | sort | uniq -d
```

Expected: No output from last command (no duplicates)

## Troubleshooting Tests

### API Connection

```python
import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GNEWS_API_KEY')

if not api_key:
    print("ERROR: API key not set")
    exit(1)

url = 'https://gnews.io/api/v4/top-headlines'
params = {
    'category': 'general',
    'country': 'us',
    'lang': 'en',
    'max': 1,
    'apikey': api_key
}

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    print("API connection: OK")
    print(f"Response: {response.status_code}")
except Exception as e:
    print(f"API connection failed: {e}")
```

### CSV Write Permission

```python
import os

test_file = 'test_write.csv'
try:
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print("Write permission: OK")
except Exception as e:
    print(f"Write permission failed: {e}")
```

### Python Version

```bash
python --version
# Should be 3.7 or higher
```

## Summary

Run this checklist before considering the pipeline ready:

- [ ] CSV created with 9 columns
- [ ] No duplicate rows detected
- [ ] All fields have values (no empty cells)
- [ ] Second run adds only new headlines
- [ ] Filtered CSV created correctly
- [ ] All 8 questions answered
- [ ] Performance is 10-30 seconds
- [ ] No errors with valid API key
- [ ] Error messages display correctly
