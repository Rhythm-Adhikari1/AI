import requests

# Fetch the list of users from JSONPlaceholder API
response = requests.get('https://jsonplaceholder.typicode.com/users')

# Check if the request was successful
if response.status_code == 200:
    users = response.json()
    
    # Loop through the JSON and print name + email + city
    
    print("USER INFORMATION FROM JSONPlaceholder API")
    
    
    for user in users:
        name = user.get('name', 'N/A')
        email = user.get('email', 'N/A')
        city = user.get('address', {}).get('city', 'N/A')
        
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"City: {city}")
        print("-" * 70)
else:
    print(f"Error: Failed to fetch data. Status code: {response.status_code}")
