# Adding a New Partner - Template

This guide explains how to add a new partner (e.g., Amazon, eBay, Shopify) to the transformer.

## Overview

Each partner has:
1. A configuration file: `partners/{partner_name}/config.py`
2. An output directory: `output/{partner_name}/`
3. An output file: `output/{partner_name}/partner.xml`

The main `transform.py` script dynamically loads partner configurations and generates outputs.

## Step-by-Step Guide

### Step 1: Create Partner Directory Structure

```bash
mkdir -p partners/amazon
mkdir -p output/amazon
touch partners/amazon/__init__.py
touch partners/amazon/config.py
```

### Step 2: Create `partners/amazon/__init__.py`

This file can be empty or contain a docstring:

```python
# Partner: Amazon
```

### Step 3: Create `partners/amazon/config.py`

This is where all partner-specific configuration goes. Here's a complete template:

```python
"""
Amazon Partner Configuration

Defines the source feed URL, XML mappings, and output schema for Amazon.
"""

# ============================================================================
# SOURCE FEED CONFIGURATION
# ============================================================================

# URL of the source XML feed
SOURCE_FEED_URL = "https://amazon.example.com/feed.xml"

# XML namespace(s) used in the source feed
# Can have multiple namespaces
SOURCE_NAMESPACE = {
    'sc': 'http://schemas.summercart.com/dealer/v1',
    # 'other': 'http://other-namespace.com',
}

# ============================================================================
# FIELD MAPPINGS
# ============================================================================

# XPath expressions to extract data from source products
# The dict key becomes the key in product_data dict passed to transform_product()
# The dict value is an XPath expression to extract the value
#
# Example XPaths:
#   './/sc:ProductCode/text()' - Get text of ProductCode element
#   './/sc:Price/sc:USD/text()' - Get nested element text
#   './/sc:Tags/sc:Tag[contains(text(), "Featured")]/text()' - Conditional
#   './/sc:InStock/@value' - Get attribute value
#
FIELD_MAPPINGS = {
    'sku': './/sc:ProductCode/text()',
    'name': './/sc:ProductName/sc:EN/text()',  # English name
    'price': './/sc:ProductPrice/text()',
    'quantity_label': './/sc:ProductQuantityLabel/text()',
    # Add any other fields you want to extract:
    # 'description': './/sc:ProductDescription/sc:EN/text()',
    # 'brand': './/sc:BrandName/text()',
    # 'category': './/sc:CategoryPath/text()',
}

# ============================================================================
# STOCK MAPPING
# ============================================================================

# Map source quantity_label values to stock availability (1=in stock, 0=out)
STOCK_MAPPING = {
    'instock': '1',
    'outofstock': '0',
    'discontinued': '0',
    'preorder': '1',
}

# ============================================================================
# DEFAULT VALUES
# ============================================================================

# Default values for fields if they're missing in source
DEFAULTS = {
    'sku': '',
    'name': '',
    'price': '0',
    'stock': '0',
}

# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

# Define the output XML structure
# Format: (xml_tag_name, is_required)
# If a required field is empty, the product is skipped
OUTPUT_SCHEMA = [
    ('ProductID', True),      # Required
    ('Title', True),          # Required
    ('Price', True),          # Required
    ('InStock', False),       # Optional
    ('Description', False),   # Optional
]

# Root element name for output XML
OUTPUT_ROOT_ELEMENT = 'AmazonCatalog'

# Product element name for output XML
OUTPUT_PRODUCT_ELEMENT = 'Product'

# ============================================================================
# TRANSFORMATION LOGIC
# ============================================================================

def transform_product(product_data: dict) -> dict:
    """
    Transform extracted product data to output format.
    
    This is where you apply partner-specific logic like:
    - Formatting prices
    - Converting units
    - Mapping categories
    - Cleaning text
    - Calculating derived values
    
    Args:
        product_data: Dict with keys from FIELD_MAPPINGS, values from source XML
        
    Returns:
        Dict with keys matching OUTPUT_SCHEMA, ready for XML output
        
    Example values in product_data:
        {
            'sku': 'PROD-123',
            'name': 'Blue Widget',
            'price': '49.99',
            'quantity_label': 'InStock',
        }
    """
    
    # Determine stock availability
    quantity_label = product_data.get('quantity_label', '').lower()
    stock = STOCK_MAPPING.get(quantity_label, '0')
    
    return {
        'ProductID': product_data.get('sku', DEFAULTS['sku']),
        'Title': product_data.get('name', DEFAULTS['name']),
        'Price': product_data.get('price', DEFAULTS['price']),
        'InStock': 'Yes' if stock == '1' else 'No',
        'Description': '',  # Could extract from product_data if you added it
    }
```

### Step 4: Run the Transformer

Test your new partner configuration:

```bash
python transform.py amazon
```

Check the output:

```bash
cat output/amazon/partner.xml
```

### Step 5: Adjust Configuration Based on Results

If the transformation didn't work as expected:

1. **Check the logs** - The script logs what it found and transformed
2. **Verify source structure** - Use a tool like XMLLint to inspect source XML
3. **Update XPath expressions** - Adjust FIELD_MAPPINGS to match actual structure
4. **Test iteratively** - Run `python transform.py amazon` after each change

## Advanced Examples

### Example: Price Formatting

```python
def transform_product(product_data: dict) -> dict:
    # Format price to 2 decimal places
    try:
        price = float(product_data.get('price', '0'))
        formatted_price = f"{price:.2f}"
    except ValueError:
        formatted_price = "0.00"
    
    return {
        'ProductID': product_data.get('sku', ''),
        'Title': product_data.get('name', ''),
        'Price': formatted_price,
        'InStock': 'Yes' if product_data.get('stock', '0') == '1' else 'No',
    }
```

### Example: Text Cleanup and Validation

```python
def transform_product(product_data: dict) -> dict:
    # Remove extra whitespace from name
    name = product_data.get('name', '').strip()
    
    # Only include product if name is not empty
    if not name:
        return {}  # Empty dict signals product should be skipped
    
    return {
        'ProductID': product_data.get('sku', ''),
        'Title': name,
        'Price': product_data.get('price', '0'),
        'InStock': 'Yes' if product_data.get('quantity_label', '').lower() == 'instock' else 'No',
    }
```

### Example: Additional Fields Extraction

If your partner needs more fields, add them to FIELD_MAPPINGS:

```python
FIELD_MAPPINGS = {
    'sku': './/sc:ProductCode/text()',
    'name': './/sc:ProductName/sc:EN/text()',
    'price': './/sc:ProductPrice/text()',
    'quantity_label': './/sc:ProductQuantityLabel/text()',
    'description': './/sc:ProductDescription/sc:EN/text()',  # NEW
    'brand': './/sc:BrandName/text()',                        # NEW
    'category': './/sc:PrimaryCategory/text()',              # NEW
}

OUTPUT_SCHEMA = [
    ('ProductID', True),
    ('Title', True),
    ('Price', True),
    ('InStock', False),
    ('Description', False),  # NEW
    ('Brand', False),        # NEW
    ('Category', False),     # NEW
]

def transform_product(product_data: dict) -> dict:
    return {
        'ProductID': product_data.get('sku', ''),
        'Title': product_data.get('name', ''),
        'Price': product_data.get('price', '0'),
        'InStock': 'Yes' if product_data.get('quantity_label', '').lower() == 'instock' else 'No',
        'Description': product_data.get('description', ''),
        'Brand': product_data.get('brand', ''),
        'Category': product_data.get('category', ''),
    }
```

## Testing Checklist

After creating a new partner:

- [ ] Partner directory created: `partners/{name}/`
- [ ] `config.py` created with all required variables
- [ ] `__init__.py` created (can be empty)
- [ ] Output directory created: `output/{name}/`
- [ ] Script runs without errors: `python transform.py {name}`
- [ ] Output file created: `output/{name}/partner.xml`
- [ ] Output XML is valid and well-formed
- [ ] Output contains expected products
- [ ] All required fields are populated
- [ ] Price formatting is correct
- [ ] Stock status mapping works

## Debugging Tips

### Script says "No products found"

- The XPath expressions don't match your source structure
- Verify source XML has products under a `Products` element
- Check namespace prefix in XPath (should match your namespace dict)

Example:
```python
# If source has namespace, use prefix in XPath:
# <sc:Products xmlns:sc="http://example.com">
#   <sc:Product>...</sc:Product>
# </sc:Products>

SOURCE_NAMESPACE = {'sc': 'http://example.com'}
# XPath must use prefix:
'.//sc:Products/sc:Product'  # CORRECT
'.//Products/Product'         # WRONG - ignores namespace
```

### Products are included but fields are empty

- The XPath expression for that field doesn't match the source
- Use a browser or XML editor to inspect actual structure
- Test XPath expressions: `product.xpath('your_xpath', namespaces=SOURCE_NAMESPACE)`

### XML output is malformed

- Ensure all values are strings (or convert with `str()`)
- Check for characters that need XML escaping (lxml handles this)
- Validate with: `xmllint --format output/{name}/partner.xml`

## Integration with GitHub Actions

Once your partner is tested locally, the GitHub Actions workflow will automatically run it.

To transform multiple partners hourly, modify `.github/workflows/feed.yml`:

```yaml
- name: Run transformations for all partners
  run: |
    python transform.py ozone
    python transform.py amazon
    python transform.py ebay
```

Or create separate jobs per partner for parallelization.

## Summary

The key files for a new partner:

1. **partners/{name}/config.py** - All configuration, field mappings, transformation logic
2. **output/{name}/partner.xml** - Auto-generated output (you don't create this)

Everything else is handled by the main `transform.py` script, which:
- Loads your partner config
- Fetches the source XML
- Parses it safely
- Extracts fields using your XPath expressions
- Calls your `transform_product()` function
- Writes the output XML

Good luck! 🚀
