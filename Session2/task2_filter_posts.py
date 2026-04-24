import csv

# Read posts.csv
filtered = []
with open('posts.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    for row in reader:
        title = row[1]
        words = len(title.split())
        
        if words > 5:
            filtered.append(row)

# Write filtered posts
with open('filtered_posts.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(filtered)

print("Filtered posts saved to filtered_posts.csv")
print("Total posts with title > 5 words: " + str(len(filtered)))
