# Auto-Update Setup for News Dashboard

## Overview
This project now automatically converts CSV files to JSON when you update CSV files in the `scrapped_output/` folder on GitHub.

## How It Works

1. **CSV Files**: Place your data files in `scrapped_output/` with the naming format: `DD.MM.YYYY.csv`
   - Example: `22.08.2025.csv`, `23.08.2025.csv`

2. **GitHub Actions**: When you push changes to CSV files, a workflow automatically:
   - Runs the `build.py` script
   - Converts CSV data to JSON files in the `api/` directory
   - Commits and pushes the generated JSON files back to the repository

3. **Frontend**: The dashboard loads data from JSON files, so updates are immediately visible

## File Structure

```
scrapped_output/          # CSV source files
├── 22.08.2025.csv       # Your CSV data
└── 23.08.2025.csv

api/                      # Auto-generated JSON files (don't edit manually)
├── available-dates.json  # List of available dates
├── company-news-2025-08-22.json
├── company-details-2025-08-22-COMPANY.json
└── ...
```

## CSV Format Requirements

Your CSV files must have exactly these columns:
- `Company_Name`: Name of the company
- `Extracted_Links`: Links related to the company news (can be "No links found")
- `Extracted_Text`: News content or "No significant news..."

## Manual Build (if needed)

If you need to build locally:
```bash
python build.py
```

## Important Notes

1. **Don't edit JSON files directly** - they're auto-generated
2. **CSV files must be properly formatted** - no Git merge conflicts
3. **File names matter** - use DD.MM.YYYY.csv format
4. **GitHub Actions permissions** are configured for automatic commits

## Troubleshooting

- If the workflow fails, check the Actions tab in your GitHub repository
- Ensure CSV files don't contain Git merge conflict markers (`<<<<<<< HEAD`)
- Company names with special characters are automatically sanitized for filenames