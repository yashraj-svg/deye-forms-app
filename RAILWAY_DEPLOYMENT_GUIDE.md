# Deploying Deye Web App to Railway with GitHub

## Overview
Railway is the simplest way to deploy Django applications publicly. It automatically detects Django apps and handles deployment with minimal configuration.

**Why Railway?**
- ✅ Free tier available ($5 credit/month)
- ✅ Automatic Django detection
- ✅ PostgreSQL database included
- ✅ Automatic SSL certificates
- ✅ GitHub integration (auto-deploy on push)
- ✅ Environment management
- ✅ Real-time logs and monitoring

---

## Step 1: Push Your Project to GitHub

### 1.1 Create a GitHub Repository
1. Go to [github.com](https://github.com) and sign in
2. Click **New Repository**
3. Name: `deye-web-app` (or your preferred name)
4. Make it **Public** (required for free Railway deployment)
5. Click **Create Repository**

### 1.2 Push Your Code to GitHub

In your project directory, run these commands:

```bash
git init
git add .
git commit -m "Initial commit: Deye Web App Project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/deye-web-app.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## Step 2: Prepare Your Django App for Production

### 2.1 Update `requirements.txt`

Your current requirements.txt should include these production packages:

```
Django==5.2.7
gunicorn
psycopg[binary,pool]
whitenoise
openpyxl
pgeocode
pillow
```

Run this to update:
```bash
pip freeze > requirements.txt
```

### 2.2 Update `deye_config/settings.py`

Add production configurations:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Set default environment variables
os.environ.setdefault("SECRET_KEY", "your-secret-key-change-in-production")
os.environ.setdefault("PGDATABASE", "railway")
os.environ.setdefault("PGUSER", "postgres")
os.environ.setdefault("PGPASSWORD", "")
os.environ.setdefault("PGHOST", "localhost")
os.environ.setdefault("PGPORT", "5432")

# Secret key - use environment variable in production
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')

# Debug mode - MUST be False in production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Allowed hosts - add your Railway domain
ALLOWED_HOSTS = ['*']

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE', 'railway'),
        'USER': os.environ.get('PGUSER', 'postgres'),
        'PASSWORD': os.environ.get('PGPASSWORD', ''),
        'HOST': os.environ.get('PGHOST', 'localhost'),
        'PORT': os.environ.get('PGPORT', '5432'),
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Middleware - Add WhiteNoise for static files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### 2.3 Create a Procfile

Create a file named `Procfile` in your project root (same directory as manage.py):

```
release: python manage.py migrate
web: gunicorn deye_config.wsgi
```

This tells Railway how to run your app and perform migrations.

### 2.4 Create a .railwayignore File

Create `.railwayignore` in project root to exclude unnecessary files:

```
__pycache__
*.pyc
.git
.gitignore
.venv
node_modules
db.sqlite3
.env.local
*.log
```

### 2.5 Commit These Changes

```bash
git add -A
git commit -m "Add production configuration and Procfile"
git push
```

---

## Step 3: Deploy on Railway

### 3.1 Create a Railway Account

1. Go to [railway.com](https://railway.com)
2. Click **Start Project** → **Create Account**
3. Sign in with GitHub (recommended for seamless integration)

### 3.2 Create a New Project

1. Go to [railway.com/new](https://railway.com/new)
2. Click **Deploy from GitHub repo**
3. Select your GitHub account and choose your `deye-web-app` repository
4. Click **Deploy Now**

Railway will automatically detect it's a Django app and create a service.

### 3.3 Add PostgreSQL Database

1. In the Railway dashboard, click **Create** button on the canvas
2. Select **Database** → **Add PostgreSQL**
3. Click **Deploy**

Railway will provision a PostgreSQL database automatically.

---

## Step 4: Configure Environment Variables

### 4.1 Set Up Variables

In the Railway dashboard:

1. Click on your **App Service** (not the database)
2. Go to **Variables** tab
3. Add these variables:

| Variable | Value |
|----------|-------|
| `DEBUG` | `False` |
| `SECRET_KEY` | Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `PGDATABASE` | `${{Postgres.PGDATABASE}}` |
| `PGUSER` | `${{Postgres.PGUSER}}` |
| `PGPASSWORD` | `${{Postgres.PGPASSWORD}}` |
| `PGHOST` | `${{Postgres.PGHOST}}` |
| `PGPORT` | `${{Postgres.PGPORT}}` |

The `${{Postgres.XXX}}` syntax references the PostgreSQL service variables automatically.

### 4.2 Generate Secret Key

Run this locally to generate a secure key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it as the `SECRET_KEY` value in Railway.

---

## Step 5: Deploy and Verify

### 5.1 Trigger Deployment

1. Click **Deploy** button in Railway dashboard (or auto-deploys on git push)
2. Watch the build logs in real-time
3. Wait for the green checkmark indicating successful deployment

### 5.2 Generate Public URL

1. Click on your app service
2. Go to **Settings** tab → **Networking** section
3. Click **Generate Domain**
4. Copy the public URL (e.g., `https://deye-web-app-production.railway.app`)

### 5.3 Verify Deployment

1. Visit your public URL in a browser
2. You should see your Deye Web App running live
3. Check logs if there are any issues: Click **View logs**

---

## Step 6: Set Up Auto-Deployment from GitHub

Railway automatically deploys when you push to GitHub:

1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add -A
   git commit -m "Your changes"
   git push origin main
   ```
3. Railway detects the push and automatically redeploys
4. Check deployment status in the Railway dashboard

---

## Troubleshooting

### Issue: Build Fails with "ModuleNotFoundError"

**Solution:** Ensure all dependencies are in `requirements.txt`:
```bash
pip freeze > requirements.txt
git add requirements.txt
git push
```

### Issue: Database Connection Error

**Solution:** Verify environment variables are correctly set:
1. Click Variables tab on your service
2. Make sure all `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT` are set
3. Click Deploy to apply changes

### Issue: Static Files Not Loading

**Solution:** Ensure WhiteNoise middleware is in settings.py and run:
```bash
python manage.py collectstatic
git push
```

### Issue: 500 Error on App

**Solution:** Check logs:
1. Click **View logs** in Railway dashboard
2. Scroll to find the error message
3. Fix and push to GitHub

### Issue: Can't Connect to Database

**Solution:**
1. Run migrations manually in Railway:
   - Click your app service
   - Go to Deployments tab
   - Click the latest deployment
   - Look for migration logs
2. Or trigger migration via Procfile `release` command

---

## Useful Railway Commands (Optional CLI)

Install Railway CLI for advanced management:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from CLI
railway up

# View logs
railway logs

# Set environment variable
railway variables set KEY=VALUE
```

---

## Best Practices for Production

✅ **Do:**
- Set `DEBUG = False` in production
- Use strong `SECRET_KEY`
- Keep your GitHub repository public for free tier
- Monitor logs regularly
- Set up email alerts for deployments
- Use PostgreSQL (not SQLite) in production
- Enable SSL/TLS (automatic on Railway)
- Regular database backups

❌ **Don't:**
- Hardcode sensitive data in code
- Use SQLite in production
- Share your Railway project link widely
- Deploy without testing locally
- Ignore deployment logs

---

## Monitoring Your Deployed App

### View Logs
- Railway dashboard → App Service → **View logs**

### Monitor Performance
- Click **Observability** to see metrics
- Check CPU, Memory, and Network usage

### Check Recent Deployments
- Click **Deployments** tab
- See history of all deployments
- Rollback to previous version if needed

---

## Custom Domain (Optional)

To use your own domain instead of Railway's subdomain:

1. Get your Railway domain: `https://deye-web-app-production.railway.app`
2. In your domain registrar (GoDaddy, Namecheap, etc.)
3. Add CNAME record pointing to Railway domain
4. Railway will automatically generate SSL certificate

---

## Next Steps

After deployment is live:

1. **Backup Database** - Set up automatic backups
2. **Error Tracking** - Consider adding Sentry for error monitoring
3. **Email Service** - Set up email backend (SendGrid, Mailgun)
4. **Analytics** - Add Google Analytics to track usage
5. **Custom Domain** - Point your own domain to the app
6. **Team Collaboration** - Invite team members to Railway project

---

## Summary

| Step | Action | Status |
|------|--------|--------|
| 1 | Push code to GitHub | ⚠️ Pending |
| 2 | Prepare Django for production | ⚠️ Pending |
| 3 | Create Railway account | ⚠️ Pending |
| 4 | Deploy from GitHub | ⚠️ Pending |
| 5 | Add PostgreSQL database | ⚠️ Pending |
| 6 | Configure environment variables | ⚠️ Pending |
| 7 | Generate public URL | ⚠️ Pending |
| 8 | Test application | ⚠️ Pending |
| 9 | Set up auto-deployment | ⚠️ Pending |

**Estimated Time:** 15-30 minutes

---

## Support

- **Railway Docs:** [docs.railway.com](https://docs.railway.com)
- **Railway Community:** [Discord](https://discord.gg/railway)
- **Django Docs:** [docs.djangoproject.com](https://docs.djangoproject.com)

Good luck with your deployment! 🚀
