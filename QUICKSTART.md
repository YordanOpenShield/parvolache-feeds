# Quick Start Guide

## Project Overview

This is a **multi-partner XML feed transformer** that automatically transforms XML feeds from various sources into partner-specific formats and publishes them to GitHub Pages hourly.

**Current Status**: ✓ Ozone partner configured and tested  
**Architecture**: Scalable, partner-agnostic core with modular partner configs

## Quick Test (Local)

```bash
# Prerequisites installed? (Python 3.11+, dependencies)
pip install -r requirements.txt

# Transform ozone feed
python transform.py

# Or explicitly:
python transform.py ozone

# Check output
cat output/ozone/partner.xml
```

**Expected result**: XML file with 5,000+ products in 10 seconds

## Directory Map

```
parvolache-ozone-feed/
├── transform.py              ← Main script (multi-partner aware)
├── partners/                 ← Partner configurations
│   └── ozone/
│       ├── __init__.py
│       └── config.py        ← URL, field mappings, schema, transform logic
├── output/                   ← Generated feeds (auto-created)
│   └── ozone/
│       └── partner.xml
├── requirements.txt         ← Dependencies (lxml, requests)
├── .github/workflows/
│   └── feed.yml             ← GitHub Actions (hourly automation)
├── README.md                ← Full documentation
├── DEPLOYMENT_GUIDE.md      ← GitHub setup steps
├── PARTNERS_TEMPLATE.md     ← How to add new partners
├── REFACTORING_NOTES.md     ← Architecture details
└── .gitignore
```

## Key Concepts

### 1. Partner Configuration
Each partner is defined in `partners/{partner_name}/config.py`:

```python
# Source
SOURCE_FEED_URL = "https://..."

# Extraction (XPath expressions)
FIELD_MAPPINGS = {
    'sku': './/sc:ProductCode/text()',
    'name': './/sc:ProductName/sc:BG/text()',
    'price': './/sc:ProductPrice/text()',
    'quantity_label': './/sc:ProductQuantityLabel/text()',
}

# Output schema
OUTPUT_SCHEMA = [
    ('SKU', True),
    ('Name', True),
    ('Price', True),
    ('Stock', False),
]

# Custom transformation
def transform_product(product_data: dict) -> dict:
    return { ... }
```

### 2. Main Script
`transform.py` is partner-agnostic:
- Loads partner config dynamically
- Fetches source XML
- Parses & validates
- Transforms using partner logic
- Writes output

```bash
python transform.py ozone   # Uses partners/ozone/config.py
python transform.py amazon  # Would use partners/amazon/config.py
```

### 3. Workflow
GitHub Actions runs hourly:
```yaml
- python transform.py ozone
- (optional) python transform.py amazon
- Commit changes
- Publish output/ to GitHub Pages
```

All partner feeds accessible at:
```
https://{user}.github.io/{repo}/ozone/partner.xml
https://{user}.github.io/{repo}/amazon/partner.xml
```

## Common Tasks

### Run Locally
```bash
python transform.py ozone
```

### Test Different Partner (if exists)
```bash
python transform.py amazon
```

### Add New Partner
See [PARTNERS_TEMPLATE.md](PARTNERS_TEMPLATE.md)

Quick version:
1. `mkdir -p partners/amazon output/amazon`
2. Create `partners/amazon/config.py` (copy from ozone)
3. Update source URL and field mappings
4. Run `python transform.py amazon`

### Deploy to GitHub
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

Quick version:
1. Push to GitHub
2. Settings > Pages > Deploy from gh-pages branch
3. Settings > Actions > "Read and write permissions"
4. Done! Workflow runs automatically hourly

### Modify Ozone Config
Edit `partners/ozone/config.py`:
- Change `SOURCE_FEED_URL`
- Update `FIELD_MAPPINGS` for different source structure
- Customize `OUTPUT_SCHEMA` for different output format
- Implement `transform_product()` for complex logic

### Check Logs
Push to GitHub and view **Actions** tab to see execution logs.

Local: `python transform.py` shows all logs to console.

## Architecture Decisions

### Why This Structure?
1. **Scalability**: Add partner = add 1 file, no core changes
2. **Maintainability**: Bug fix in core helps all partners
3. **Flexibility**: Each partner can be completely different
4. **Simplicity**: No database, no API, no complexity

### What's the Core Script Doing?
- Loading partner config
- Fetching XML safely (with timeout)
- Parsing XML (lxml for safety)
- Extracting fields (XPath)
- Applying partner transformation
- Writing XML output

### What's the Config Doing?
- Defining source URL
- Defining field extraction (XPath)
- Defining output structure
- Implementing custom transformation

## Files at a Glance

| File | Purpose | Edit If... |
|---|---|---|
| `transform.py` | Core orchestrator | Core logic changes (rarely) |
| `partners/ozone/config.py` | Ozone config | Changing ozone source/output |
| `partners/{new}/config.py` | New partner | Adding new partner |
| `.github/workflows/feed.yml` | Automation | Changing schedule/partners |
| `README.md` | Full docs | Need detailed info |
| `PARTNERS_TEMPLATE.md` | Partner guide | Adding new partner |

## Debugging

### "No products found"
- XPath expressions don't match source structure
- Check source XML with browser/XMLLint
- Update FIELD_MAPPINGS

### "Field is empty"
- XPath for that field doesn't match
- Verify with: `element.xpath('your_xpath', namespaces=...)`
- Common issue: namespace prefix in XPath

### Workflow doesn't run
- Check Settings > Actions > General > Workflow permissions
- Must have "Read and write permissions"

### Feed not on GitHub Pages
- Check Settings > Pages > source = gh-pages branch
- Workflow must complete successfully
- Usually takes <30 seconds to publish

## Next Steps

1. **Deploy**: Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. **Verify**: Check GitHub Actions workflow runs hourly
3. **Monitor**: Visit `https://{user}.github.io/{repo}/ozone/partner.xml`
4. **Expand**: Add new partners as needed using [PARTNERS_TEMPLATE.md](PARTNERS_TEMPLATE.md)

## Support

- **Main docs**: [README.md](README.md)
- **Deployment help**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Adding partners**: [PARTNERS_TEMPLATE.md](PARTNERS_TEMPLATE.md)
- **Architecture**: [REFACTORING_NOTES.md](REFACTORING_NOTES.md)

---

**Status**: Production Ready  
**Last Tested**: February 1, 2026  
**Ozone Partner**: ✓ Working (5,483 products)
