# Company News Dashboard

A dynamic web dashboard for displaying daily company news data from CSV files, deployed on Netlify with automatic updates.

## 🚀 Features

- **Daily CSV Processing**: Automatically processes CSV files with company news data
- **Interactive Dashboard**: Clean, modern interface to browse companies and their news
- **Real-time Updates**: Dashboard automatically refreshes when new CSV files are added
- **Search Functionality**: Filter companies by name
- **Responsive Design**: Works on desktop and mobile devices
- **Public Access**: Hosted on Netlify with a public URL

## 📁 Project Structure

```
NewsDashboard/
├── index.html                 # Frontend dashboard
├── .netlify/functions/        # Serverless API functions
│   ├── available-dates.py     # Get available CSV dates
│   ├── company-news.py        # Get companies list for date
│   └── company-details.py     # Get specific company details
├── scrapped_output/           # CSV files storage
├── .github/workflows/         # Automation workflows
├── netlify.toml              # Netlify configuration
├── upload-csv.py             # Manual CSV upload script
└── requirements.txt          # Python dependencies
```

## 🔧 Setup and Deployment

### 1. Deploy to Netlify

1. **Connect to GitHub**:
   - Push this repository to GitHub
   - Connect your GitHub repo to Netlify
   - Netlify will automatically detect the `netlify.toml` configuration

2. **Automatic Deployment**:
   - Any push to the main branch triggers automatic deployment
   - CSV files in `scrapped_output/` are included in the deployment

### 2. Daily Data Updates

You have **3 options** for updating CSV data daily:

#### Option A: Manual Upload (Recommended for start)
```bash
# Upload a new CSV file
python upload-csv.py path/to/your/daily_data.csv

# This will:
# 1. Copy CSV to scrapped_output/ with today's date
# 2. Commit changes to git
# 3. Push to GitHub (triggers Netlify deployment)
```

#### Option B: Automated GitHub Actions (Set up once)
- The workflow in `.github/workflows/update-csv.yml` runs daily
- Modify the workflow to download from your data source
- Or manually commit CSV files to trigger updates

#### Option C: API Integration
- Modify the serverless functions to fetch data from your API
- No CSV files needed - data fetched in real-time

## 📊 CSV File Format

Your CSV files should have these columns:
- `Company_Name`: Name of the company
- `Extracted_Text`: News content or "No significant corporate developments..."
- `Extracted_Links`: Related news links (optional)

Example filename: `22.08.2025.csv` (DD.MM.YYYY format)

## 🌐 Usage

1. **Access Dashboard**: Visit your Netlify public URL
2. **Select Date**: Use the date picker to choose a day
3. **Browse Companies**: Companies are categorized as "With News" or "No Significant News"  
4. **View Details**: Click any company to see full news content and links

## 🔄 How Daily Updates Work

1. **New CSV File**: You add a new CSV file (manually or automated)
2. **Git Commit**: Changes are committed to your repository
3. **Auto Deploy**: Netlify detects the changes and redeploys
4. **Data Refresh**: Dashboard automatically shows the new data
5. **Public Access**: Users see updated data immediately

## ⚙️ Configuration

### Netlify Settings
- **Build Command**: `echo 'Static site deployment'`
- **Publish Directory**: `.` (root)
- **Functions Directory**: `.netlify/functions`

### Environment Variables (if needed)
No environment variables required for basic setup.

## 🚨 Important Notes

- **File Naming**: CSV files must follow `DD.MM.YYYY.csv` format
- **Data Processing**: The system automatically categorizes companies with/without news
- **Performance**: Serverless functions handle the data processing efficiently
- **Cost**: Netlify free tier supports most use cases

## 📞 Support

For issues with:
- **Deployment**: Check Netlify deployment logs
- **Data Processing**: Verify CSV format and file naming
- **API Errors**: Check Netlify function logs

## 🔗 Public URL

Once deployed, your dashboard will be available at:
`https://your-site-name.netlify.app`

Share this URL with anyone who needs access to the daily company news dashboard!