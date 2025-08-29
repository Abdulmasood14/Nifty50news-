#!/usr/bin/env python3
"""
Simple CSV server that processes CSV files directly and serves JSON endpoints
This eliminates the need for pre-generated JSON files
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pandas as pd
import os
import glob
import re
from datetime import datetime
from urllib.parse import urlparse

class CSVHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        try:
            if path == '/api/available-dates':
                self.serve_available_dates()
            elif path.startswith('/api/company-news-'):
                date = path.replace('/api/company-news-', '').replace('.json', '')
                self.serve_company_news(date)
            elif path.startswith('/api/company-details-'):
                parts = path.replace('/api/company-details-', '').replace('.json', '').split('-')
                if len(parts) >= 4:  # date parts + company name
                    date = f"{parts[0]}-{parts[1]}-{parts[2]}"
                    company = '-'.join(parts[3:])
                    self.serve_company_details(date, company)
                else:
                    self.send_error(400, "Invalid company details URL format")
            elif path == '/' or path == '/index.html':
                self.serve_static_file('index.html')
            else:
                # Try to serve static files
                file_path = path.lstrip('/')
                if os.path.exists(file_path):
                    self.serve_static_file(file_path)
                else:
                    self.send_error(404, "File not found")
        except Exception as e:
            print(f"Error handling {path}: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def serve_available_dates(self):
        """Serve available dates from CSV files"""
        csv_files = glob.glob('scrapped_output/*.csv')
        dates = []
        
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            parsed_date = self.parse_date_from_filename(filename)
            if parsed_date:
                dates.append({
                    'date': parsed_date,
                    'filename': filename,
                    'display_date': datetime.strptime(parsed_date, '%Y-%m-%d').strftime('%A, %B %d, %Y')
                })
        
        dates.sort(key=lambda x: x['date'], reverse=True)
        
        self.send_json_response(dates)

    def serve_company_news(self, date):
        """Serve company news for a specific date"""
        csv_file = self.find_csv_for_date(date)
        if not csv_file:
            self.send_error(404, f"No data found for date {date}")
            return
        
        try:
            # Read CSV with proper handling
            df = pd.read_csv(csv_file, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
            df.columns = df.columns.str.strip()
            
            companies_with_news = []
            companies_no_news = []
            
            for _, row in df.iterrows():
                company_name = str(row['Company_Name']).strip()
                
                # Skip corrupted data
                if (len(company_name) > 50 or 
                    company_name.startswith(('=======', '<<<<<<<', '>>>>>>>'))):
                    continue
                
                extracted_text = str(row['Extracted_Text']).strip() if 'Extracted_Text' in row else ''
                extracted_links = str(row['Extracted_Links']).strip() if 'Extracted_Links' in row else ''
                
                # Categorize news
                has_news = self.has_significant_news(extracted_text)
                
                company_data = {
                    'name': company_name,
                    'text': extracted_text,
                    'links_raw': extracted_links,
                    'has_content': len(extracted_text) > 0
                }
                
                if has_news:
                    companies_with_news.append(company_data)
                else:
                    companies_no_news.append(company_data)
            
            # Sort companies
            companies_with_news.sort(key=lambda x: x['name'])
            companies_no_news.sort(key=lambda x: x['name'])
            
            response_data = {
                'date': date,
                'companies_with_news': companies_with_news,
                'companies_no_news': companies_no_news,
                'total_companies': len(companies_with_news) + len(companies_no_news),
                'news_count': len(companies_with_news),
                'no_news_count': len(companies_no_news)
            }
            
            self.send_json_response(response_data)
            
        except Exception as e:
            self.send_error(500, f"Error processing CSV: {str(e)}")

    def serve_company_details(self, date, company):
        """Serve detailed company information"""
        csv_file = self.find_csv_for_date(date)
        if not csv_file:
            self.send_error(404, f"No data found for date {date}")
            return
        
        try:
            df = pd.read_csv(csv_file, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
            df.columns = df.columns.str.strip()
            
            # Find the company (case-insensitive partial match)
            company_row = None
            for _, row in df.iterrows():
                row_company = str(row['Company_Name']).strip()
                if company.lower() in row_company.lower() or row_company.lower() in company.lower():
                    company_row = row
                    break
            
            if company_row is None:
                self.send_error(404, f"Company {company} not found for date {date}")
                return
            
            # Extract company details
            company_name = str(company_row['Company_Name']).strip()
            extracted_text = str(company_row['Extracted_Text']).strip() if 'Extracted_Text' in company_row else ''
            extracted_links = str(company_row['Extracted_Links']).strip() if 'Extracted_Links' in company_row else ''
            
            # Process links
            processed_links = self.process_links(extracted_links)
            
            details = {
                'company_name': company_name,
                'extracted_text': extracted_text,
                'links_raw': extracted_links,
                'processed_links': processed_links,
                'date': date
            }
            
            self.send_json_response(details)
            
        except Exception as e:
            self.send_error(500, f"Error processing company details: {str(e)}")

    def serve_static_file(self, file_path):
        """Serve static files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine content type
            if file_path.endswith('.html'):
                content_type = 'text/html'
            elif file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            else:
                content_type = 'text/plain'
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error serving static file: {str(e)}")

    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def parse_date_from_filename(self, filename):
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

    def find_csv_for_date(self, date):
        """Find CSV file for a given date"""
        # Convert YYYY-MM-DD to DD.MM.YYYY
        try:
            year, month, day = date.split('-')
            csv_filename = f"{day.lstrip('0')}.{month.lstrip('0')}.{year}.csv"
            csv_path = f"scrapped_output/{csv_filename}"
            
            if os.path.exists(csv_path):
                return csv_path
        except:
            pass
        return None

    def has_significant_news(self, text):
        """Determine if company has significant news"""
        if not text or len(text.strip()) < 50:
            return False
        
        text_lower = text.lower()
        no_news_patterns = [
            "no significant corporate developments",
            "no significant news",
            "no news",
            "no updates",
            "no recent news",
            "no major news",
            "nothing significant",
            "no developments",
            "no announcements"
        ]
        
        for pattern in no_news_patterns:
            if pattern in text_lower:
                return False
        
        return True

    def process_links(self, links_str):
        """Process and clean links from CSV"""
        if not links_str or links_str.lower().startswith('no links found'):
            return []
        
        # Extract URLs using regex
        url_pattern = r'https?://[^\s"\'<>\])]+'
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

def main():
    """Start the server"""
    port = 8000
    server = HTTPServer(('localhost', port), CSVHandler)
    print(f"[SERVER] CSV Server running at http://localhost:{port}")
    print("[INFO] Serving CSV files directly from scrapped_output/")
    print("[INFO] Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped")
        server.shutdown()

if __name__ == '__main__':
    main()