import requests
import csv

# Get posts from API
response = requests.get('https://jsonplaceholder.typicode.com/posts')

if response.status_code == 200:
    posts = response.json()
    
    # Save to CSV file
    with open('posts.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'body'])
        
        for post in posts:
            writer.writerow([post['id'], post['title'], post['body']])
    
    print("Saved posts to posts.csv")
else:
    print("Error getting posts")
