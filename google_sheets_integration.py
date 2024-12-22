import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# Replace with the path to your JSON key
SERVICE_ACCOUNT_FILE = 'G:/My Drive/ExpenseTracker/service-account-key.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Authenticate
import os
import json
from google.oauth2.service_account import Credentials

# Use credentials from the environment variable
credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not credentials_json:
    raise ValueError("Google credentials not found in environment variables.")
credentials = Credentials.from_service_account_info(json.loads(credentials_json), scopes=SCOPES)
client = gspread.authorize(credentials)

# Replace with your spreadsheet ID
SPREADSHEET_ID = '1v9U7LvKVqFmB1YM-4sIbEzwf70zPbGWLJUchNn1fLwE'

# Keywords for categorizing expenses
CATEGORY_KEYWORDS = {
    "COGS (売上原価)": ["raw materials", "inventory", "supplies"],
    "SG&A (販売費及び一般管理費)": ["general expenses", "admin expenses", "sg&a"],
    "Entertainment (交際費)": ["dinner", "lunch", "entertainment"],
    "Employee Compensation (給与費)": ["salary", "wages", "payroll"],
    "Depreciation (減価償却費)": ["depreciation", "amortization"],
    "Rent (賃貸料)": ["rent", "lease"],
    "Interest (利子費用)": ["interest", "loan interest"],
    "Taxes (税金及び公課)": ["tax", "registration fee"],
    "R&D (研究開発費)": ["research", "development", "r&d"],
    "Advertising (広告費)": ["advertising", "marketing"],
    "Repairs (修繕費)": ["repair", "maintenance"],
    "Utilities (光熱費)": ["electricity", "water", "internet", "utility"],
    "Insurance (保険料)": ["insurance", "policy"],
    "Bad Debts (貸倒損失)": ["bad debt", "write-off"]
}

# Column mapping for tax categories
CATEGORY_COLUMNS = {
    "COGS (売上原価)": 4,
    "SG&A (販売費及び一般管理費)": 5,
    "Entertainment (交際費)": 6,
    "Employee Compensation (給与費)": 7,
    "Depreciation (減価償却費)": 8,
    "Rent (賃貸料)": 9,
    "Interest (利子費用)": 10,
    "Taxes (税金及び公課)": 11,
    "R&D (研究開発費)": 12,
    "Advertising (広告費)": 13,
    "Repairs (修繕費)": 14,
    "Utilities (光熱費)": 15,
    "Insurance (保険料)": 16,
    "Bad Debts (貸倒損失)": 17,
}

def categorize_expense(description):
    """Determine the category based on the description."""
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.lower() in description.lower() for keyword in keywords):
            return category
    return "Miscellaneous"

def insert_expense(date, amount, description, payment_type):
    """Insert the expense data into the Google Sheet."""
    try:
        # Connect to the spreadsheet
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1

        # Fetch current data to determine the next available row
        all_values = sheet.get_all_values()
        next_row = len(all_values) + 1 if len(all_values) >= 6 else 6

        # Categorize the expense
        category = categorize_expense(description)
        category_column = CATEGORY_COLUMNS.get(category, 17)  # Default to column Q for Miscellaneous

        # Prepare data for insertion
        row_data = [''] * 19  # Create a blank row
        row_data[2] = date  # Column C
        row_data[category_column - 1] = amount  # Correct tax category column
        row_data[17] = payment_type  # Column R
        row_data[18] = description  # Column S

        # Update the row in the sheet
        sheet.update(range_name=f"A{next_row}:S{next_row}", values=[row_data])
        print(f"Data inserted successfully in row {next_row}!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Example input from ChatGPT (simulated dictation)
    user_input = "Paid 5000 yen for team lunch on 2024-12-25 via card."

    # Extract details from input
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", user_input)
    date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    amount_match = re.search(r"(\d+) yen", user_input)
    amount = int(amount_match.group(1)) if amount_match else 0

    payment_type_match = re.search(r"via (\w+)", user_input)
    payment_type = payment_type_match.group(1).capitalize() if payment_type_match else "Unknown"

    description_match = re.search(r"for (.+?) on", user_input)
    description = description_match.group(1).strip() if description_match else "No description provided"

    # Insert into the Google Sheet
    insert_expense(date, amount, description, payment_type)
