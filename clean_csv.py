#!/usr/bin/env python3
"""
Script to clean CSV files by removing Git merge conflicts
"""

import os
import re

def clean_csv_file(file_path):
    """Clean a single CSV file by removing merge conflict markers"""
    print(f"Cleaning {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Remove Git merge conflict markers and their content
    # Remove lines that start with <<<<<<< HEAD
    content = re.sub(r'^<<<<<<< HEAD.*?\n', '', content, flags=re.MULTILINE)
    
    # Remove lines that start with =======
    content = re.sub(r'^=======.*?\n', '', content, flags=re.MULTILINE)
    
    # Remove lines that start with >>>>>>> [commit hash]
    content = re.sub(r'^>>>>>>> [a-f0-9]+.*?\n', '', content, flags=re.MULTILINE)
    
    # Remove any duplicate lines that might have been created
    lines = content.split('\n')
    cleaned_lines = []
    prev_line = ""
    
    for line in lines:
        # Skip if it's the same as previous line (removes duplicates from merge conflicts)
        if line.strip() != prev_line.strip() or line.strip() == "":
            cleaned_lines.append(line)
        prev_line = line
    
    # Write cleaned content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print(f"[OK] Cleaned {file_path}")

def main():
    csv_folder = 'scrapped_output'
    if os.path.exists(csv_folder):
        for file in os.listdir(csv_folder):
            if file.endswith('.csv'):
                file_path = os.path.join(csv_folder, file)
                clean_csv_file(file_path)
        print("[SUCCESS] All CSV files cleaned!")
    else:
        print(f"[ERROR] Folder {csv_folder} not found!")

if __name__ == '__main__':
    main()