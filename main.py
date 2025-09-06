from utils.processing_utils import generate_text_files, delete_statements, process_bank_statement, \
    process_credit_card_statement
from utils.google_utils import update_google_sheet, get_google_sheets_data
import os
import json

# directory paths
def return_directory_paths():
    """
    Function to return the directory paths for the folders where the files will live
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    statements_dir = os.path.join(parent_dir, "statements")
    text_statements_dir = os.path.join(parent_dir, "text_statements")

    return statements_dir, text_statements_dir

def main():
    
    ### GOOGLE SHEETS UPDATE ###
    with open('google_sheets_data.json', 'r') as file:
        google_sheets_data = json.load(file)

    budget_sheet_id = google_sheets_data['budget']['sheet_id']
    budget_input_range = google_sheets_data['budget']['input_range']
    budget_category_range = google_sheets_data['budget']['categories_range']

    # gets the informatuion for the categories for the transactions
    category_info = get_google_sheets_data(budget_sheet_id, budget_category_range)

    category_dict = {}
    for category in category_info:
        if len(category) >= 2:
            category_dict[category[0]] = category[1].strip().split(',')

    # processes any new documents in the file
    statements_dir, text_statements_dir = return_directory_paths()
    generate_text_files(statements_dir, text_statements_dir)

    # deletes the statements after they have been processed
    delete_statements(statements_dir)

    # processes information in the text files
    data_upload = []
    for filename in os.listdir(text_statements_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(text_statements_dir, filename)
            statement_type = filename.split('_')[0]
            if statement_type == "bank-of-america":
                data = process_bank_statement(filepath)
            elif statement_type == "chase":
                data = process_credit_card_statement(filepath)

            print("Transaction Complete:")
            print(data)

        # categorizes the transactions
        for transaction in data:
            for key, value in category_dict.items():
                if any(x.lower().strip() in transaction[2].lower() and x != '' for x in value):
                    transaction[1] = key
                    continue
    
        data_upload += data
    
    delete_statements(text_statements_dir)

    old_transaction_data = get_google_sheets_data(budget_sheet_id, budget_input_range)

    update_google_sheet(budget_sheet_id, budget_input_range, old_transaction_data + data_upload)

if __name__ == "__main__":
    main()
