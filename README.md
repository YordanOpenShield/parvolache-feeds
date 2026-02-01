# XML Feed Transformer

A simple, serverless static XML feed transformer that fetches a source XML feed, transforms it into partner-specific schemas, and publishes them to GitHub Pages. Runs automatically every hour via GitHub Actions. **Supports multiple partners** with easy configuration.

## Features

✓ **Multi-Partner Support** - Easily add new partners by creating partner configs
✓ **Static Output** - No runtime server required
✓ **Automated** - Runs hourly via GitHub Actions cron job
✓ **Simple** - Pure Python with minimal dependencies (lxml, requests)
✓ **Reliable** - Validates XML, fails loudly on errors
✓ **Maintainable** - Clean, modular code with detailed logging
✓ **Accessible** - Published to GitHub Pages with HTTPS

## Repository Structure

```
parvolache-ozone-feed/
├── transform.py              # Main transformation orchestrator
├── requirements.txt          # Python dependencies
├── partners/                 # Partner configurations
│   ├── ozone/
│   │   ├── __init__.py
│   │   └── config.py        # Ozone-specific configuration
│   └── [future_partner]/
│       ├── __init__.py
│       └── config.py        # Partner-specific configuration
├── output/                   # Generated outputs
│   ├── ozone/
│   │   └── partner.xml      # Ozone feed
│   └── [future_partner]/
│       └── partner.xml      # Partner feed
├── .github/
│   └── workflows/
│       └── feed.yml         # GitHub Actions workflow
└── README.md
```

## Setup

### 1. Prerequisites

- Python 3.11+ (for local testing)
- GitHub repository with Actions enabled
- GitHub Pages enabled (Settings > Pages > Source: gh-pages branch)

### 2. Installation

Clone or create the repository:

```bash
git clone <repository-url>
cd parvolache-ozone-feed
```

Install dependencies locally (optional, for testing):

```bash
pip install -r requirements.txt
```

### 3. Configuration (Ozone Partner)

The ozone partner is pre-configured. Edit `partners/ozone/config.py` to customize:

- **SOURCE_FEED_URL** - URL of your source XML feed
- **FIELD_MAPPINGS** - XPath expressions to extract product data
- **OUTPUT_SCHEMA** - Define output XML structure
- **transform_product()** - Custom transformation logic

### 4. Enable GitHub Pages

1. Go to repository **Settings > Pages**
2. Set **Source** to `Deploy from a branch`
3. Select branch: `gh-pages` (created automatically by workflow)
4. Save

### 5. Push to GitHub

```bash
git add .
git commit -m "Initial commit: XML feed transformer"
git push origin main
```

## Running Locally

Test the transformation script locally:

```bash
# Transform ozone feed (explicit)
python transform.py ozone

# Transform ozone feed (default)
python transform.py

# Transform another partner (if configured)
python transform.py amazon
```

This will:
1. Load the partner configuration
2. Fetch the source XML feed
3. Parse and validate it
4. Transform to partner schema
5. Write to `output/{partner}/partner.xml`
6. Log detailed progress to stdout

## Adding New Partners

### Step 1: Create Partner Directory

```bash
mkdir -p partners/amazon
touch partners/amazon/__init__.py
touch partners/amazon/config.py
```

### Step 2: Configure Partner

Edit `partners/amazon/config.py`:

```python
"""Amazon Partner Configuration"""

SOURCE_FEED_URL = "https://amazon.example.com/feed.xml"

SOURCE_NAMESPACE = {
    'sc': 'http://schemas.summercart.com/dealer/v1'  # Or your namespace
}

# Map XPath expressions to field names
FIELD_MAPPINGS = {
    'sku': './/sc:ProductCode/text()',
    'name': './/sc:ProductName/sc:BG/text()',
    'price': './/sc:ProductPrice/text()',
    'quantity_label': './/sc:ProductQuantityLabel/text()',
}

STOCK_MAPPING = {
    'instock': '1',
    'outofstock': '0',
}

DEFAULTS = {
    'sku': '',
    'name': '',
    'price': '0',
    'stock': '0',
}

# Amazon might want different fields or structure
OUTPUT_SCHEMA = [
    ('ProductID', True),
    ('Title', True),
    ('MSRP', True),
    ('Availability', False),
]

OUTPUT_ROOT_ELEMENT = 'AmazonProducts'
OUTPUT_PRODUCT_ELEMENT = 'Item'

def transform_product(product_data: dict) -> dict:
    """Custom transformation for Amazon format"""
    quantity_label = product_data.get('quantity_label', '').lower()
    stock = STOCK_MAPPING.get(quantity_label, '0')
    
    return {
        'ProductID': product_data.get('sku', DEFAULTS['sku']),
        'Title': product_data.get('name', DEFAULTS['name']),
        'MSRP': product_data.get('price', DEFAULTS['price']),
        'Availability': 'In Stock' if stock == '1' else 'Out of Stock',
    }
```

### Step 3: Create Output Directory

```bash
mkdir -p output/amazon
```

### Step 4: Test

```bash
python transform.py amazon
```

Check `output/amazon/partner.xml` for the transformed feed.

## Accessing the Feeds

Once deployed, the transformed feeds are available at:

```
https://<github-username>.github.io/<repo-name>/ozone/partner.xml
https://<github-username>.github.io/<repo-name>/amazon/partner.xml
# ... etc for each partner
```

Example:
```
https://yordan-github.github.io/parvolache-ozone-feed/ozone/partner.xml
https://yordan-github.github.io/parvolache-ozone-feed/amazon/partner.xml
```

## How It Works

### Automatic Workflow

The `.github/workflows/feed.yml` workflow:

1. **Triggers** - Every hour at 00 minutes (hourly cron job), or manually via `workflow_dispatch`
2. **Checks out** the repository
3. **Sets up** Python 3.11
4. **Installs** dependencies
5. **Runs** the transformation script (defaults to ozone, or specify a partner)
6. **Commits** changes to `output/` (if any feeds changed)
7. **Publishes** the entire `output/` directory to GitHub Pages

### Manual Trigger

You can also manually trigger the workflow for a specific partner:

1. Go to **Actions** tab in your repository
2. Select **Transform XML Feed** workflow
3. Click **Run workflow**
4. (Optional) Enter partner name, or leave blank for "ozone"

### Multi-Partner Automation

To transform multiple partners automatically, you can:

**Option 1:** Modify the workflow to run multiple partner transformations in sequence

```yaml
- name: Run transformations for all partners
  run: |
    python transform.py ozone
    python transform.py amazon
    python transform.py ebay
```

**Option 2:** Create a separate workflow job per partner

```yaml
jobs:
  transform-ozone:
    runs-on: ubuntu-latest
    steps:
      - ...
      - run: python transform.py ozone
  
  transform-amazon:
    runs-on: ubuntu-latest
    steps:
      - ...
      - run: python transform.py amazon
```

## Output Schemas

### Ozone Partner (Default)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Products>
  <Product>
    <SKU>PRODUCT-123</SKU>
    <Name>Product Name</Name>
    <Price>99.99</Price>
    <Stock>1</Stock>
  </Product>
</Products>
```

**Fields:**
- `SKU` - Product code/SKU
- `Name` - Product name
- `Price` - Product price
- `Stock` - Stock status (1 = in stock, 0 = out of stock)

Each partner can have a completely different output schema defined in their `config.py`.

## Logging

The script logs all operations to stdout with timestamps:

```
2024-02-01 12:00:00 [INFO] ============================================================
2024-02-01 12:00:00 [INFO] Starting XML Feed Transformation
2024-02-01 12:00:00 [INFO] Time: 2024-02-01T12:00:00.123456
2024-02-01 12:00:00 [INFO] ============================================================
2024-02-01 12:00:01 [INFO] Fetching source feed from: https://example.com/feed.xml
2024-02-01 12:00:02 [INFO] Successfully fetched feed (45678 bytes)
2024-02-01 12:00:02 [INFO] Parsing source XML...
2024-02-01 12:00:02 [INFO] Successfully parsed source XML
2024-02-01 12:00:02 [INFO] Transforming feed to partner schema...
2024-02-01 12:00:02 [INFO] Found 250 products to transform
2024-02-01 12:00:02 [INFO] Successfully transformed 248 products
2024-02-01 12:00:02 [INFO] Writing output to: output/partner.xml
2024-02-01 12:00:02 [INFO] Successfully wrote output (18920 bytes)
2024-02-01 12:00:02 [INFO] ============================================================
2024-02-01 12:00:02 [INFO] ✓ Feed transformation completed successfully
2024-02-01 12:00:02 [INFO] ============================================================
```

## Error Handling

The script **fails loudly** with non-zero exit codes:

- **Source unreachable** (timeout, 404, etc.) → `exit(1)`
- **XML parsing fails** → `exit(1)`
- **File write fails** → `exit(1)`
- **Unexpected errors** → `exit(1)` with traceback

GitHub Actions will report the failure in the workflow run details.

## Customization

### Modifying Ozone Configuration

Edit `partners/ozone/config.py`:

1. **Update source feed URL**
   ```python
   SOURCE_FEED_URL = "https://your-new-source-feed-url.com/feed.xml"
   ```

2. **Update XPath mappings** to match your source XML structure
   ```python
   FIELD_MAPPINGS = {
       'sku': './/sc:ProductID/text()',          # Changed
       'name': './/sc:ProductTitle/sc:EN/text()',  # Changed
       'price': './/sc:CatalogPrice/text()',    # Changed
       'quantity_label': './/sc:Availability/text()',  # Changed
   }
   ```

3. **Customize output schema**
   ```python
   OUTPUT_SCHEMA = [
       ('SKU', True),
       ('Name', True),
       ('Price', True),
       ('Stock', False),
       ('Description', False),      # New field
       ('Category', False),          # New field
   ]
   ```

4. **Implement custom transformation logic**
   ```python
   def transform_product(product_data: dict) -> dict:
       # Apply any complex transformations
       # Price might need conversion, names need cleanup, etc.
       return {
           'SKU': product_data.get('sku', '').upper(),  # Uppercase SKU
           'Name': product_data.get('name', '').title(),  # Title case
           'Price': f"${float(product_data.get('price', 0)):.2f}",  # Format
           'Stock': '1' if product_data.get('quantity_label', '').lower() == 'instock' else '0',
           'Description': '',
           'Category': '',
       }
   ```

### Changing the Cron Schedule

Edit `.github/workflows/feed.yml`:

```yaml
on:
  schedule:
    # Run every 30 minutes
    - cron: '*/30 * * * *'
```

Common cron patterns:
- `0 * * * *` - Every hour at :00
- `0 */2 * * *` - Every 2 hours
- `0 9 * * *` - Daily at 9 AM UTC
- `0 0 * * 0` - Weekly (Sunday at midnight UTC)

## Dependencies

- **lxml** - Fast, reliable XML processing
- **requests** - HTTP library for fetching remote feeds
- **Python 3.11** - Runtime

See `requirements.txt` for pinned versions.

## Troubleshooting

### Workflow Fails to Run

**Check:** Settings > Actions > General
- Ensure "Workflow permissions" includes "Read and write permissions"

### GitHub Pages Not Updating

**Check:** Settings > Pages > Build and deployment
- Ensure "Source" is set to `gh-pages` branch
- Workflow may need `permissions: pages: write`

### XML Parsing Fails

**Debug locally:**
```bash
python transform.py
# Check the logged error message
```

**Common causes:**
- Source feed is invalid XML
- Source URL is unreachable
- Network timeout (increase timeout in `requests.get()`)

### Feed URL Unreachable

**Verify:**
```bash
curl -I "https://your-source-feed-url"
```

**Check:**
- URL is correct and accessible
- No authentication required (or update script to handle auth)
- No geoblocking

## Security Notes

- GitHub Actions uses `GITHUB_TOKEN` (temporary, auto-generated)
- No manual credentials stored
- Source feed URL is visible in repository (consider if sensitive)
- Output is published publicly on GitHub Pages

## Performance

- **Fetch time** - Typically 1-3 seconds
- **Parse time** - Depends on feed size, typically <1 second
- **Transform time** - Typically <1 second
- **Total runtime** - Usually 30-60 seconds per workflow run

## Examples

See `output/partner.xml` for a sample of the generated output.

## License

This project is provided as-is. Modify as needed for your use case.

## Support

For issues:
1. Check the GitHub Actions workflow logs: **Actions** tab > workflow run
2. Run locally: `python transform.py` and check output
3. Verify XML syntax of source feed
4. Check network connectivity to source URL

---

**Last updated:** February 1, 2024
