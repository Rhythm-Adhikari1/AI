import requests
import csv

# Fetch posts from the JSONPlaceholder API
response = requests.get('https://jsonplaceholder.typicode.com/posts')

if response.status_code == 200:
    posts = response.json()
    
    # Save to posts.csv with id, title, body columns
    with open('posts.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'title', 'body']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for post in posts:
            writer.writerow({
                'id': post['id'],
                'title': post['title'],
                'body': post['body']
            })
    
    print(f" Successfully saved {len(posts)} posts to posts.csv")
else:
    print(f"Error: Failed to fetch posts. Status code: {response.status_code}")
