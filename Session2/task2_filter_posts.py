import csv

# Read posts.csv and filter posts with titles having more than 5 words
filtered_posts = []

with open('posts.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        # Count words in title
        word_count = len(row['title'].split())
        
        # Filter posts with more than 5 words in title
        if word_count > 5:
            filtered_posts.append(row)

# Write filtered results to filtered_posts.csv
if filtered_posts:
    with open('filtered_posts.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'title', 'body']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(filtered_posts)
    
    print(f" Successfully filtered and saved {len(filtered_posts)} posts to filtered_posts.csv")
    print("\nSample of filtered posts:")
    print("-" * 80)
    for i, post in enumerate(filtered_posts[:3], 1):
        word_count = len(post['title'].split())
        print(f"\n{i}. ID: {post['id']} (Title words: {word_count})")
        print(f"   Title: {post['title']}")
        print(f"   Body (first 100 chars): {post['body'][:100]}...")
else:
    print("No posts found with titles having more than 5 words.")
