# GitHub Actions Setup Guide

## Overview
This workflow automatically updates your Garmin data daily by:
1. Running extraction scripts to fetch new data from Garmin
2. Enriching activities with weather data
3. Running dbt models to transform the data
4. Committing the updated database back to GitHub

## Setup Steps

### 1. Add GitHub Secrets
You need to add your API credentials as GitHub Secrets:

1. Go to your repository on GitHub
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add these two secrets:

   | Secret Name | Value |
   |------------|-------|
   | `GARMIN_EMAIL` | Your Garmin Connect email |
   | `GARMIN_PASSWORD` | Your Garmin Connect password |

### 2. Commit and Push the Workflow

```bash
git add .github/
git commit -m "Add GitHub Actions workflow for automated data updates"
git push
```

### 3. Commit Your Database (First Time Only)

If you haven't already committed your database to GitHub:

```bash
git add data/garmin.db
git commit -m "Add Garmin database"
git push
```

### 4. Verify the Workflow

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You should see the "Update Garmin Data" workflow listed

### 5. Manual Trigger (Optional)

To test the workflow before waiting for the scheduled run:

1. Go to **Actions** tab
2. Click "Update Garmin Data" workflow
3. Click "Run workflow" dropdown
4. Click the green "Run workflow" button

## Schedule

The workflow runs daily at **6 AM UTC**. To change the schedule:

1. Edit `.github/workflows/update_garmin_data.yml`
2. Modify the cron expression:
   ```yaml
   - cron: '0 6 * * *'  # minute hour day month day-of-week
   ```

**Examples:**
- `'0 8 * * *'` - 8 AM UTC daily
- `'0 0 * * 0'` - Midnight UTC every Sunday
- `'0 */6 * * *'` - Every 6 hours

Use [crontab.guru](https://crontab.guru/) to help create cron expressions.

## Pulling Updates to Your Local Machine

After GitHub Actions updates your database:

```bash
git pull
```

This will sync the updated database to your local machine so you can view it in your Streamlit dashboard.

## Monitoring

- Check the **Actions** tab to see workflow runs
- Click on any run to see detailed logs
- You'll receive email notifications if workflows fail (configurable in GitHub settings)

## Troubleshooting

**Workflow fails with authentication error:**
- Verify your GitHub Secrets are correct
- Check if your Garmin password has changed

**Workflow fails on dbt step:**
- Check if dbt profile is correctly configured
- Ensure dbt models are compatible with dbt-sqlite

**Database conflicts when pulling:**
- Commit or stash your local changes first
- Use `git pull --rebase` if needed
