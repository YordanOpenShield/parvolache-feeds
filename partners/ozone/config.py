"""
Ozone Partner Configuration

Defines the source feed URL, XML mappings, and output schema for Ozone.
"""

# Source feed configuration
SOURCE_FEED_URL = "https://parvolache.com/module.php?ModuleName=com.seliton.superxmlexport&Username=Kabit&Domain=igra4kite.com&Signature=86357b9bc6b0ff6dc7d4afd1ec953795a91c5f7f&DealerAccountType=0"

# XML namespace used in source feed
SOURCE_NAMESPACE = {
    'sc': 'http://schemas.summercart.com/dealer/v1'
}

# XPath mappings to extract data from source XML
FIELD_MAPPINGS = {
    'sku': './/sc:ProductCode/text()',
    'name': './/sc:ProductName/sc:BG/text()',
    'price': './/sc:ProductPrice/text()',
    'quantity_label': './/sc:ProductQuantityLabel/text()',
}

# Stock status mapping (map quantity_label values to stock availability)
STOCK_MAPPING = {
    'instock': '1',      # In stock
    'outofstock': '0',   # Out of stock
}

# Default values for missing fields
DEFAULTS = {
    'sku': '',
    'name': '',
    'price': '0',
    'stock': '0',
}

# Output XML schema definition
# Each field: (xml_tag, required)
OUTPUT_SCHEMA = [
    ('SKU', True),
    ('Name', True),
    ('Price', True),
    ('Stock', False),
]

# Root element name for output XML
OUTPUT_ROOT_ELEMENT = 'Products'

# Product element name for output XML
OUTPUT_PRODUCT_ELEMENT = 'Product'

def transform_product(product_data: dict) -> dict:
    """
    Transform extracted product data to output format.
    
    This function can be customized per partner for complex transformations.
    
    Args:
        product_data: Dictionary with keys matching FIELD_MAPPINGS
        
    Returns:
        Dictionary with output field names and values
    """
    # Determine stock availability
    quantity_label = product_data.get('quantity_label', '').lower()
    stock = STOCK_MAPPING.get(quantity_label, '0')
    
    return {
        'SKU': product_data.get('sku', DEFAULTS['sku']),
        'Name': product_data.get('name', DEFAULTS['name']),
        'Price': product_data.get('price', DEFAULTS['price']),
        'Stock': stock,
    }
