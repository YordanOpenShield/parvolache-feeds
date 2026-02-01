# Deployment Guide

This guide will help you deploy the XML Feed Transformer to GitHub and enable GitHub Pages hosting.

## Step 1: Push to GitHub Repository

```bash
cd parvolache-ozone-feed
git add .
git commit -m "Initial commit: Python-based XML feed transformer"
git push origin main
```

## Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** (top navigation)
3. Scroll to **Pages** section (on the left sidebar)
4. Under "Build and deployment":
   - **Source**: Select "Deploy from a branch"
   - **Branch**: Select `gh-pages` (will be created automatically)
   - **Folder**: Select `/ (root)`
5. Click **Save**

## Step 3: Configure Workflow Permissions

1. Go to **Settings > Actions > General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Check ✓ "Allow GitHub Actions to create and approve pull requests"
5. Click **Save**

## Step 4: Verify Workflow Setup

1. Go to **Actions** tab
2. You should see "Transform XML Feed" workflow
3. Click on it to see workflow definition
4. The workflow is configured to run:
   - **Automatically**: Every hour (at the top of each hour, UTC)
   - **Manually**: Via "Run workflow" button

## Step 5: Test Manually

1. Go to **Actions** tab
2. Select **Transform XML Feed** workflow
3. Click **Run workflow** button
4. Select the branch (usually `main`)
5. Click **Run workflow**

Monitor the workflow run:
- Check the logs in the "Transform" job
- Verify the "Deploy" job publishes to GitHub Pages

## Step 6: Access Your Feed

Once the workflow completes successfully, your feed will be available at:

```
https://<github-username>.github.io/<repo-name>/partner.xml
```

**Example:**
```
https://yordan-github.github.io/parvolache-ozone-feed/partner.xml
```

Test accessibility:
```bash
curl -I https://yordan-github.github.io/parvolache-ozone-feed/partner.xml
# Should return HTTP 200 OK
```

## Step 7: Verify XML is Valid

You can validate your XML feed using:

```bash
curl https://yordan-github.github.io/parvolache-ozone-feed/partner.xml | xmllint --format -
```

Or use an online XML validator:
- https://www.w3schools.com/xml/xml_validator.asp
- https://www.xmlvalidation.com/

## Troubleshooting

### Workflow doesn't run on schedule

**Issue**: The scheduled workflow doesn't trigger automatically

**Solution**:
1. Make sure GitHub Actions is enabled in Settings
2. Verify the cron syntax is correct (currently: `0 * * * *`)
3. Push a commit to trigger workflows (GitHub requires at least one event on the branch)

### GitHub Pages not deploying

**Issue**: The output directory isn't published to GitHub Pages

**Solution**:
1. Check Settings > Pages, ensure source is set to `gh-pages` branch
2. Verify the workflow has `permissions: pages: write`
3. Check the "Deploy" job logs for errors

### Feed URL returns 404

**Issue**: The `partner.xml` file is not found at the expected URL

**Solution**:
1. Check that the workflow "Deploy" job completed successfully
2. Verify your GitHub username and repository name in the URL
3. Wait a few moments for GitHub Pages to update (usually <30 seconds)

### Schedule not triggering

**Note**: GitHub Actions scheduled workflows may not run if:
- No commits have been pushed to the repository
- The repository is a fork (unless you enable "Run workflows from fork pull requests")
- The workflow file has a syntax error

**Solution**: 
- Make a commit and push it to enable scheduling
- Verify the `.github/workflows/feed.yml` file is valid

## Monitoring

### Check Workflow Runs

Go to **Actions** tab to see:
- Last run time
- Status (success/failure)
- Execution logs
- Commit messages

### Verify Output File

Check that `partner.xml` is updated:

```bash
curl -I https://yordan-github.github.io/parvolache-ozone-feed/partner.xml
# Look for the Last-Modified header
```

## Custom Configuration

### Changing the Schedule

Edit `.github/workflows/feed.yml` and update the cron expression:

```yaml
schedule:
  - cron: '*/30 * * * *'  # Run every 30 minutes
```

Common expressions:
- `0 * * * *` - Hourly
- `0 9 * * *` - Daily at 9 AM UTC
- `0 0 * * 0` - Weekly Sunday
- `0 0 1 * *` - Monthly

### Updating Source Feed URL

Edit `transform.py`:

```python
SOURCE_FEED_URL = "https://your-new-url.com/feed.xml"
```

Then push and the next workflow run will use the new URL.

## Support Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Cron Expression Generator](https://crontab.guru/)

---

**Status**: ✓ Ready for deployment
