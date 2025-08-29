#!/usr/bin/env python3
"""
Build script to convert CSV files to JSON for static serving
"""

import json
import os
import glob
import pandas as pd
import re
from datetime import datetime

def parse_date_from_filename(filename):
    """Extract date from filename like 22.08.2025.csv"""
    try:
        date_part = filename.replace('.csv', '')
        parts = date_part.split('.')
        
        if len(parts) == 3:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        pass
    return None

def categorize_company_news(extracted_text):
    """Determine if company has significant news"""
    if not extracted_text or pd.isna(extracted_text):
        return "no_news"
    
    text_str = str(extracted_text).strip().lower()
    
    no_news_patterns = [
        "no significant corporate developments for",
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
    
    date_pattern = r"no significant corporate developments for .+ on \d{2}\.\d{2}\.\d{4}"
    if re.search(date_pattern, text_str):
        return "no_news"
    
    if len(text_str) < 50:
        return "no_news"
    
    for pattern in no_news_patterns:
        if pattern in text_str:
            return "no_news"
    
    return "has_news"

def process_links(links_str):
    """Process and clean links from CSV"""
    if not links_str or pd.isna(links_str):
        return []
        
    links_str = str(links_str).strip()
    if not links_str or links_str.lower().startswith('no links found'):
        return []
    
    processed_links = []
    
    potential_links = []
    for delimiter in [',', ';', '\n', '|', '\t']:
        if delimiter in links_str:
            potential_links = [link.strip() for link in links_str.split(delimiter)]
            break
    
    if not potential_links:
        potential_links = [links_str]
    
    for link in potential_links:
        link = link.strip()
        if link and len(link) > 10:
            if not link.startswith(('http://', 'https://')):
                if link.startswith('www.'):
                    link = 'https://' + link
                elif '.' in link and not link.startswith('no '):
                    link = 'https://' + link
            
            if any(domain in link for domain in ['http', 'www.', '.com', '.org', '.net', '.in']):
                processed_links.append(link)
    
    return processed_links

def main():
    print("Building static JSON files from CSV data...")
    
    # Create api directory for JSON files
    os.makedirs('api', exist_ok=True)
    
    # Process available dates
    csv_folder = 'scrapped_output'
    if not os.path.exists(csv_folder):
        print(f"Warning: {csv_folder} folder not found")
        return
    
    csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))
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
    
    dates.sort(key=lambda x: x['date'], reverse=True)
    
    # Save available dates
    with open('api/available-dates.json', 'w') as f:
        json.dump(dates, f)
    
    print(f"Generated available-dates.json with {len(dates)} dates")
    
    # Process each CSV file
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        parsed_date = parse_date_from_filename(filename)
        if not parsed_date:
            continue
        
        print(f"Processing {filename}...")
        
        # Read and process CSV with proper handling of multiline and quoted fields
        try:
            df = pd.read_csv(file_path, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
            df.columns = df.columns.str.strip()
            print(f"Successfully loaded {len(df)} rows from {filename}")
            print(f"Columns: {df.columns.tolist()}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
        
        companies_with_news = []
        companies_no_news = []
        company_details = {}
        
        for _, row in df.iterrows():
            # Ensure we get the actual company name, not some random text
            company_name = str(row['Company_Name']).strip()
            
            # Skip if this looks like corrupted data (not a proper company name)
            if (len(company_name) > 50 or 
                company_name.startswith('=======') or 
                company_name.startswith('<<<<<<<') or
                company_name.startswith('>>>>>>>') or
                '.' in company_name[:10]):  # Skip if starts with numbers/dates
                continue
                
            extracted_text = row['Extracted_Text'] if 'Extracted_Text' in row else ''
            extracted_links = row['Extracted_Links'] if 'Extracted_Links' in row else ''
            
            # Clean up the extracted text
            extracted_text = str(extracted_text).strip() if extracted_text else ''
            
            news_category = categorize_company_news(extracted_text)
            processed_links = process_links(str(extracted_links))
            
            company_data = {
                'name': company_name,
                'text': extracted_text,
                'links_raw': str(extracted_links) if extracted_links else '',
                'has_content': len(extracted_text) > 0
            }
            
            # Detailed company data with proper company name
            company_details[company_name] = {
                'company_name': company_name,
                'extracted_text': extracted_text,
                'links_raw': str(extracted_links) if extracted_links else '',
                'processed_links': processed_links,
                'date': parsed_date
            }
            
            if news_category == "has_news":
                companies_with_news.append(company_data)
            else:
                companies_no_news.append(company_data)
        
        companies_with_news.sort(key=lambda x: x['name'])
        companies_no_news.sort(key=lambda x: x['name'])
        
        # Save company news for this date
        date_data = {
            'date': parsed_date,
            'companies_with_news': companies_with_news,
            'companies_no_news': companies_no_news,
            'total_companies': len(companies_with_news) + len(companies_no_news),
            'news_count': len(companies_with_news),
            'no_news_count': len(companies_no_news)
        }
        
        with open(f'api/company-news-{parsed_date}.json', 'w') as f:
            json.dump(date_data, f)
        
        # Save individual company details
        for company_name, details in company_details.items():
            # Create a safe filename by removing/replacing problematic characters
            safe_company_name = re.sub(r'[<>:"/\\|?*]', '_', company_name)
            safe_company_name = safe_company_name[:50]  # Limit length
            with open(f'api/company-details-{parsed_date}-{safe_company_name}.json', 'w') as f:
                json.dump(details, f)
    
    print("Build completed successfully!")

if __name__ == '__main__':
    main()