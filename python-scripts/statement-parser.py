import pdfplumber
import csv
import re
import os
import argparse
from datetime import datetime

def extract_transactions_from_pdf(pdf_path):
    """
    Extract transaction data from a bank statement PDF
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        list: List of transaction dictionaries
    """
    transactions = []
    
    # Open the PDF
    with pdfplumber.open(pdf_path) as pdf:
        # Process each page
        for page in pdf.pages:
            text = page.extract_text()
            
            # Split text into lines
            lines = text.split('\n')
            
            # Process each line to find transactions
            for line in lines:
                # Skip header lines and non-transaction lines
                # This pattern needs to be adjusted based on your specific bank statement format
                #transaction_pattern = r'(\d{2}/\d{2}/\d{2})\s+(.*?)\s+(\$?-?\d+\.\d{2})'
                transaction_pattern = re.compile(r'(\d{2}/\d{2}/\d{2,4})\s+(.*?)\s+(-?\$?[\d,]+\.\d{2})')

                match = re.search(transaction_pattern, line)
                
                if match:
                    date_str, description, amount_str = match.groups()
                    
                    # Clean up the amount (remove $ and handle negative values)
                    amount = amount_str.replace('$', '')
                    
                    # Create a transaction dictionary
                    transaction = {
                        'date': date_str,
                        'description': description.strip(),
                        'amount': amount
                    }
                    
                    transactions.append(transaction)
    
    return transactions

def save_to_csv(transactions, output_path):
    """
    Save transaction data to a CSV file
    
    Args:
        transactions (list): List of transaction dictionaries
        output_path (str): Path where CSV will be saved
    """
    if not transactions:
        print("No transactions found to save")
        return
    
    # Field names for the CSV
    fieldnames = ['date', 'description', 'amount']
    
    # Write to CSV
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)
    
    print(f"CSV file created successfully at {output_path}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert bank statement PDF to CSV')
    parser.add_argument('pdf_path', help='Path to the bank statement PDF file')
    parser.add_argument('--output', '-o', 
                        help='Output CSV file path (default: input filename with .csv extension)')
    
    args = parser.parse_args()
    
    # Validate PDF path
    if not os.path.exists(args.pdf_path):
        print(f"Error: File {args.pdf_path} does not exist.")
        return
    
    # Set default output path if not specified
    if not args.output:
        base_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        args.output = f"{base_name}_transactions.csv"
    
    # Extract and save transactions
    print(f"Processing {args.pdf_path}...")
    transactions = extract_transactions_from_pdf(args.pdf_path)
    
    print(f"Found {len(transactions)} transactions")
    save_to_csv(transactions, args.output)

if __name__ == "__main__":
    main()
