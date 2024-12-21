from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials

# Initialize Flask app
app = Flask(__name__)

# Google Sheets setup
SERVICE_ACCOUNT_FILE = 'G:/My Drive/ExpenseTracker/service-account-key.json'  # Update path if needed
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
SPREADSHEET_ID = '1v9U7LvKVqFmB1YM-4sIbEzwf70zPbGWLJUchNn1fLwE'  # Replace with your Spreadsheet ID

@app.route('/')
def home():
    return "Flask server is running!"

# Endpoint to insert expense
@app.route('/insert-expense', methods=['POST'])
def insert_expense():
    try:
        # Parse data from the request
        data = request.json
        date = data.get('date')
        amount = data.get('amount')
        description = data.get('description')
        payment_type = data.get('payment_type')
        category = data.get('category')

        # Map categories to spreadsheet columns
        CATEGORY_COLUMNS = {
            "COGS": 4,
            "SG&A": 5,
            "Entertainment": 6,
            "Employee Compensation": 7,
            "Depreciation": 8,
            "Rent": 9,
            "Interest": 10,
            "Taxes": 11,
            "R&D": 12,
            "Advertising": 13,
            "Repairs": 14,
            "Utilities": 15,
            "Insurance": 16,
            "Bad Debts": 17,
        }
        category_column = CATEGORY_COLUMNS.get(category, 17)

        # Connect to the spreadsheet and find the next row
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        all_values = sheet.get_all_values()
        next_row = len(all_values) + 1 if len(all_values) >= 6 else 6

        # Prepare data for the new row
        row_data = [''] * 19
        row_data[2] = date  # Column C
        row_data[category_column - 1] = amount  # Correct category column
        row_data[17] = payment_type  # Column R
        row_data[18] = description  # Column S

        # Insert data into the sheet
        sheet.update(f"A{next_row}:S{next_row}", [row_data])

        return jsonify({"message": "Expense added successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
