# Netlify Deployment Guide

## Quick Deploy to Netlify

### Option 1: One-Click Deploy (Recommended)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Abdulmasood14/Nifty50news-)

### Option 2: Manual Setup

1. **Go to Netlify Dashboard**
   - Visit [netlify.com](https://netlify.com) and sign in
   - Click "Add new site" → "Import an existing project"

2. **Connect Repository**
   - Choose GitHub as your Git provider
   - Select: `Abdulmasood14/Nifty50news-`

3. **Build Settings**
   - **Build command:** `python build.py`
   - **Publish directory:** `.` (root directory)
   - **Branch to deploy:** `master`

4. **Environment Variables**
   - No additional environment variables needed

5. **Deploy Site**
   - Click "Deploy site"
   - Wait for build to complete (~2-3 minutes)

## Site Configuration

### Auto-Generated Files
The following files configure Netlify deployment:
- `netlify.toml` - Main Netlify configuration
- `_redirects` - URL redirect rules
- `requirements.txt` - Python dependencies

### Features Enabled
- ✅ Static site hosting
- ✅ Custom domain support
- ✅ HTTPS/SSL certificates
- ✅ CDN and caching
- ✅ API redirects (`/api/*` routes)
- ✅ Security headers
- ✅ SPA fallback routing

## Auto-Update System

Once deployed:
1. **CSV Updates** → GitHub Actions runs `build.py`
2. **JSON Files Generated** → Committed back to repository
3. **Netlify Auto-Deploys** → Site updates automatically

## Custom Domain (Optional)

After deployment:
1. Go to your Netlify site dashboard
2. Click "Domain settings"
3. Add your custom domain
4. Follow Netlify's DNS setup instructions

## Build Process

```bash
# What happens during build:
1. Netlify pulls latest code
2. Installs Python dependencies (pandas)
3. Runs python build.py
4. Generates JSON files from CSV data
5. Serves static files with optimized caching
```

## Monitoring

- **Build logs:** Available in Netlify dashboard
- **GitHub Actions:** Monitor CSV → JSON conversion
- **Site analytics:** Available in Netlify dashboard

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check build logs in Netlify dashboard |
| Data not updating | Verify GitHub Actions completed successfully |
| API routes 404 | Check `_redirects` file and `netlify.toml` |
| Slow loading | JSON files are cached for 5 minutes |

Your site will be available at: `https://your-site-name.netlify.app`