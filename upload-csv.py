#!/usr/bin/env python3
"""
Script to upload daily CSV file and trigger Netlify deployment
Usage: python upload-csv.py path/to/your/daily.csv
"""

import sys
import os
import shutil
import subprocess
from datetime import datetime
import argparse

def upload_csv(csv_file_path):
    """Upload CSV file to scrapped_output folder and commit to git"""
    
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' not found")
        return False
    
    # Create scrapped_output directory if it doesn't exist
    output_dir = "scrapped_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with current date
    today = datetime.now().strftime("%d.%m.%Y")
    output_filename = f"{today}.csv"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        # Copy file to scrapped_output
        shutil.copy2(csv_file_path, output_path)
        print(f"✅ CSV file copied to {output_path}")
        
        # Git operations
        subprocess.run(["git", "add", output_path], check=True)
        subprocess.run([
            "git", "commit", "-m", 
            f"Update daily CSV data - {today}"
        ], check=True)
        
        print(f"✅ Changes committed to git")
        
        # Push to remote (this will trigger Netlify deployment)
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Changes pushed to remote repository")
        print(f"🚀 Netlify will automatically deploy the updated dashboard")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Upload daily CSV file and trigger deployment')
    parser.add_argument('csv_file', help='Path to the CSV file to upload')
    
    args = parser.parse_args()
    
    print(f"📊 Uploading CSV file: {args.csv_file}")
    
    if upload_csv(args.csv_file):
        print(f"\n🎉 Success! Your dashboard will be updated with the new data in a few minutes.")
        print(f"📱 Check your Netlify dashboard for deployment status.")
    else:
        print(f"\n❌ Upload failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()