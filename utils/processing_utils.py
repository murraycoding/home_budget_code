"""
Functions to process pdf statements into text. Text will be analyzed and recorded
"""
### IMPORTS ###
import os
import re
from datetime import datetime
import pymupdf
from utils.date_utils import extract_date_from_string, format_date

# Update this one later
def generate_text_files(statements_dir, text_statements_dir): # firast child functions that runs
    """
    Generates the text files to be read into the process functions
    """
    print("List of files in statements directory:")
    print(os.listdir(statements_dir))

    for filename in os.listdir(statements_dir):
        print(f"- - - - - Processing {filename} - - - - - ")
        new_file_name = generate_file_name(filename)
        if not new_file_name:
            continue

        doc = pymupdf.open(os.path.join(statements_dir, filename))

        with open(os.path.join(text_statements_dir,new_file_name), "wb") as output:
            for page in doc:
                text = page.get_text().encode("utf8")
                output.write(text)
                output.write(bytes((12,)))

def generate_file_name(filename):
    """
    Function to generate the file name for the text file

    Args:
        filename (str): The name of the file to be processed
    
    Returns:
        str: The new file name for the text file
        Will return None if the file name cannot be generated
    """
    file_indicator_dict = {
        "bank-of-america":
            {
                "file_indicator": "eStmt",
                "date_format": "YYYY-MM-DD"
            },
        "chase":
            {
                "file_indicator": "statements",
                "date_format": "YYYYMMDD"
            }
    }

    for key, value in file_indicator_dict.items():
        if value["file_indicator"] in filename:
            date_obj = extract_date_from_string(filename, date_format = value["date_format"])
            file_type = key
            new_file_name = f"{file_type}_{date_obj}.txt"
            return new_file_name

    print(f"WARNING: {filename} does not match any file indicators.")
    return None

def delete_statements(statements_dir):
    for filename in os.listdir(statements_dir):
        file_path = os.path.join(statements_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as error:
            print(f"Failed to delete {file_path}. Reason: {error}")

def process_bank_statement(file_path):
    """
    Function to process a bank statement
    """
    # opens the file
    with open(file_path, "r") as file:
        lines = file.readlines()

    ignore_transactions = ['CHASE','TRAVELERS','Banking Transfer']
    transaction_data = []
    print(f"Length of Bank statement = {len(lines)}")
    
    for n, line in enumerate(lines):
        if n < 5:
            continue
        line_three_before = str(lines[n-3].strip())
        line_two_before = str(lines[n-2].strip())
        line_one_before = str(lines[n-1].strip())
        line_now = str(lines[n].strip())

        money_detection = re.search(r'\d{1,3}(?:,\d{3})*\.\d{2}', line_now)

        if not money_detection:
            continue
        
        # looks for money
        date_pattern = re.compile(r'\b\d{2}/\d{2}/\d{2}\b')

        # looks for a date above the money line
        if date_pattern.match(line_three_before):
            transaction_text = line_two_before
            date = datetime.strptime(line_three_before, "%m/%d/%y").date()
        elif date_pattern.match(line_two_before):
            transaction_text = line_one_before
            date = datetime.strptime(line_two_before, "%m/%d/%y").date()
        else:
            continue
        
        # ignores transactions with the particular text in them
        if any(ignore_element.upper() in transaction_text.upper() for ignore_element in ignore_transactions):
            continue

        # appends the transaction data to the list
        transaction_data.append(["BANK", "category here", transaction_text, str(date), line_now])
    
    return transaction_data

def process_credit_card_statement(file_path):
    """
    Processes a credit card statement text file and returns a dictionary of transactions

    Args:
        statement_text (str): The text of the credit card statement
    
    Returns:
        dict: A dictionary of transactions
    """
    transaction_data = []
    # opens the file
    with open(file_path, "r") as file:
        lines = file.readlines()

    file_name = file_path.split('/')[-1]
    year = file_name.split('_')[1].split('.')[0].split('-')[0]
    month = file_name.split('_')[1].split('.')[0].split('-')[1]
    print(f"Filename = {file_name}")
    print(f"Year = {year}")

    # add code to add the year to a transaction date if none is present
    # function "settings"
    if "chase" in file_name:
        ignore_transactions = ['AUTOMATIC PAYMENT']
        flip_transaction_value = True
        transaction_source = "Credit Card"
    elif "bank-of-america" in file_name:
        ignore_transactions = ['CHASE','TRAVELERS','Banking Transfer']
        flip_transaction_value = False
        transaction_source = "Bank"
    else:
        ignore_transactions = []
        flip_transaction_value = False

    print(f"Length of Credit Card statement = {len(lines)}")
    
    for n, line in enumerate(lines):
        if n < 5:
            continue
        line_three_before = str(lines[n-3].strip())
        line_two_before = str(lines[n-2].strip())
        line_one_before = str(lines[n-1].strip())
        line_now = str(lines[n].strip())

        money_detection = re.search(r'\d{1,3}(?:,\d{3})*\.\d{2}', line_now)

        if not money_detection:
            continue
        
        # looks for money
        date_pattern_long = re.compile(r'\b\d{2}/\d{2}/\d{2}\b')
        date_pattern_short = re.compile(r'\b\d{2}/\d{2}\b')

        # looks for a date above the money line
        # date patterns for MM/DD/YY
        if date_pattern_long.match(line_three_before):
            transaction_text = line_two_before
            date = datetime.strptime(line_three_before, "%m/%d/%y").date()
        elif date_pattern_long.match(line_two_before):
            transaction_text = line_one_before
            date = datetime.strptime(line_two_before, "%m/%d/%y").date()
        # date patterns for MM/DD
        elif date_pattern_short.match(line_three_before):
            transaction_text = line_two_before
            if line_three_before.split('/')[0] == '12' and month == '01':
                date = datetime.strptime(line_three_before + "/" + str(int(year) - 1), "%m/%d/%Y").date()
            else:
                date = datetime.strptime(line_three_before + "/" + year, "%m/%d/%Y").date()
        elif date_pattern_short.match(line_two_before):
            transaction_text = line_one_before
            if line_two_before.split('/')[0] == '12' and month == '01':
                date = datetime.strptime(line_two_before + "/" + str(int(year) - 1), "%m/%d/%Y").date()
            else:
                date = datetime.strptime(line_two_before + "/" + year, "%m/%d/%Y").date()
        
        else:
            continue

        if flip_transaction_value:
            transaction_value = float(line_now.replace(',', '').replace('$','')) * -1
        else:
            transaction_value = float(line_now.replace(',', ''))
        
        # ignores transactions with the particular text in them
        if any(ignore_element.upper() in transaction_text.upper() for ignore_element in ignore_transactions):
            continue

        # appends the transaction data to the list
        transaction_data.append([transaction_source, "category here", transaction_text, str(date), transaction_value])
    
    return transaction_data
