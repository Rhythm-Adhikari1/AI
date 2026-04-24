import requests
import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get posts from API
api_url = os.getenv('JSONPLACEHOLDER_API_URL')
response = requests.get(f'{api_url}/posts')

if response.status_code == 200:
    posts = response.json()
    
    # Save to CSV file
    output_file = os.getenv('OUTPUT_POSTS_CSV')
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'body'])
        
        for post in posts:
            writer.writerow([post['id'], post['title'], post['body']])
    
    print(f"Saved posts to {output_file}")
else:
    print("Error getting posts")
