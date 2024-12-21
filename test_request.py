import requests

# URL of the Flask endpoint
url = "http://127.0.0.1:5000/insert-expense"

# Data to send in the POST request
data = {
    "date": "2024-12-25",
    "amount": 5000,
    "description": "team lunch",
    "payment_type": "card",
    "category": "Entertainment"
}

# Send the POST request
response = requests.post(url, json=data)

# Print the response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
