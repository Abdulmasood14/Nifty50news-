from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import pandas as pd
import os
import glob
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

# Configuration
CSV_FOLDER = 'scrapped_output'
STATIC_FOLDER = 'static'

def parse_date_from_filename(filename):
    """Extract date from filename like 22.08.2025.csv"""
    try:
        # Remove .csv extension and split by dots
        date_part = filename.replace('.csv', '')
        parts = date_part.split('.')
        
        if len(parts) == 3:
            day, month, year = parts
            # Convert to standard date format
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        pass
    return None

def process_links(links_str):
    """Process and clean links from CSV"""
    if not links_str or pd.isna(links_str):
        return []
        
    links_str = str(links_str).strip()
    if not links_str or links_str.lower().startswith('no links found'):
        return []
    
    # Use regex to extract all URLs from the text
    url_pattern = r'https?://[^\s"\'<>\])\n]*'
    urls = re.findall(url_pattern, links_str)
    
    # Clean and deduplicate
    clean_urls = []
    seen = set()
    
    for url in urls:
        # Remove trailing punctuation
        url = re.sub(r'[.,;)}\]]+$', '', url)
        if url and url not in seen and len(url) > 10:
            clean_urls.append(url)
            seen.add(url)
    
    return clean_urls

def categorize_company_news(extracted_text):
    """Determine if company has significant news"""
    if not extracted_text or pd.isna(extracted_text):
        return "no_news"
    
    text_str = str(extracted_text).strip().lower()
    
    # Specific patterns based on your actual CSV data
    no_news_patterns = [
        "no significant corporate developments for",  # Your exact pattern
        "no significant corporate developments",
        "no significant developments", 
        "no significant news",
        "no significant",
        "no news found",
        "no news",
        "no updates",
        "no recent news",
        "no major news",
        "nothing significant",
        "no developments",
        "no announcements"
    ]
    
    # Check for the specific date pattern in your data
    date_pattern = r"no significant corporate developments for .+ on \d{2}\.\d{2}\.\d{4}"
    if re.search(date_pattern, text_str):
        return "no_news"
    
    # If text is very short (less than 50 characters), likely no news
    if len(text_str) < 50:
        return "no_news"
    
    # Check for no news patterns
    for pattern in no_news_patterns:
        if pattern in text_str:
            return "no_news"
    
    # If we reach here, assume there's actual news content
    return "has_news"

@app.route('/')
def serve_index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/available-dates')
def get_available_dates():
    """Get list of available dates from CSV files"""
    try:
        if not os.path.exists(CSV_FOLDER):
            return jsonify([])
        
        csv_files = glob.glob(os.path.join(CSV_FOLDER, '*.csv'))
        dates = []
        
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            parsed_date = parse_date_from_filename(filename)
            if parsed_date:
                dates.append({
                    'date': parsed_date,
                    'filename': filename,
                    'display_date': datetime.strptime(parsed_date, '%Y-%m-%d').strftime('%A, %B %d, %Y')
                })
        
        # Sort dates in descending order (newest first)
        dates.sort(key=lambda x: x['date'], reverse=True)
        return jsonify(dates)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/company-news/<date>')
def get_company_news(date):
    """Get company news data for a specific date"""
    try:
        # Find CSV file for the given date
        csv_files = glob.glob(os.path.join(CSV_FOLDER, '*.csv'))
        target_file = None
        
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            parsed_date = parse_date_from_filename(filename)
            if parsed_date == date:
                target_file = file_path
                break
        
        if not target_file:
            return jsonify({'error': 'No data found for this date'}), 404
        
        # Read and process CSV with proper multiline handling
        df = pd.read_csv(target_file, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
        
        # Clean column names (remove whitespace)
        df.columns = df.columns.str.strip()
        
        companies_with_news = []
        companies_no_news = []
        
        for _, row in df.iterrows():
            company_name = str(row['Company_Name']).strip()
            
            # Skip invalid company names (corrupted data)
            if (len(company_name) > 50 or 
                pd.isna(row['Company_Name']) or
                company_name.startswith(('=======', '<<<<<<<', '>>>>>>>'))):
                continue
            
            extracted_text = str(row['Extracted_Text']).strip() if 'Extracted_Text' in row and pd.notna(row['Extracted_Text']) else ''
            extracted_links = str(row['Extracted_Links']).strip() if 'Extracted_Links' in row and pd.notna(row['Extracted_Links']) else ''
            
            news_category = categorize_company_news(extracted_text)
            
            # Process links properly
            processed_links = process_links(extracted_links)
            
            company_data = {
                'name': company_name,
                'text': extracted_text,
                'links': processed_links,
                'has_content': len(extracted_text) > 0
            }
            
            if news_category == "has_news":
                companies_with_news.append(company_data)
            else:
                companies_no_news.append(company_data)
        
        # Sort alphabetically within each category
        companies_with_news.sort(key=lambda x: x['name'])
        companies_no_news.sort(key=lambda x: x['name'])
        
        result = {
            'date': date,
            'companies_with_news': companies_with_news,
            'companies_no_news': companies_no_news,
            'total_companies': len(companies_with_news) + len(companies_no_news),
            'news_count': len(companies_with_news),
            'no_news_count': len(companies_no_news)
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/company-details/<date>/<company_name>')
def get_company_details(date, company_name):
    """Get detailed news content for a specific company"""
    try:
        # Find and read CSV file
        csv_files = glob.glob(os.path.join(CSV_FOLDER, '*.csv'))
        target_file = None
        
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            parsed_date = parse_date_from_filename(filename)
            if parsed_date == date:
                target_file = file_path
                break
        
        if not target_file:
            return jsonify({'error': 'No data found for this date'}), 404
        
        df = pd.read_csv(target_file)
        df.columns = df.columns.str.strip()
        
        # Find the specific company
        company_row = df[df['Company_Name'].str.strip() == company_name]
        
        if company_row.empty:
            return jsonify({'error': 'Company not found'}), 404
        
        row = company_row.iloc[0]
        
        # Process links for this specific company
        processed_links = process_links(str(row['Extracted_Links']) if 'Extracted_Links' in row else '')
        
        return jsonify({
            'company_name': company_name,
            'extracted_text': str(row['Extracted_Text']) if 'Extracted_Text' in row else '',
            'links_raw': str(row['Extracted_Links']) if 'Extracted_Links' in row else '',  # Added this line
            'processed_links': processed_links,
            'date': date
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(CSV_FOLDER, exist_ok=True)
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    
    print(f"Starting Company News Dashboard...")
    print(f"CSV folder: {CSV_FOLDER}")
    print(f"Looking for CSV files...")
    
    # Check for existing CSV files
    csv_files = glob.glob(os.path.join(CSV_FOLDER, '*.csv'))
    if csv_files:
        print(f"Found {len(csv_files)} CSV files:")
        for file in csv_files:
            print(f"  - {os.path.basename(file)}")
    else:
        print(f"No CSV files found in {CSV_FOLDER} folder")
    
    app.run(debug=True, host='0.0.0.0', port=5000)