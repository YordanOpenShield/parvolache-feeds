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
    'catalog_num': './/sc:ProductCode/text()',
    'name': './/sc:ProductName/sc:BG/text()',
    'price': './/sc:ProductPrice/text()',
    'price_client': './/sc:ProductDistributorPrice/text()',
    'quantity_label': './/sc:ProductQuantityLabel/text()',
    'barcode': './/sc:ProductBarcode/text()',
    'brand': './/sc:BrandName/sc:BG/text()',
    'category': './/sc:CategoryPath/sc:BG/text()',
    'color': './/sc:Color/sc:BG/text()',
}

# Stock status mapping (map quantity_label values to stock availability text)
STOCK_MAPPING = {
    'instock': 'Да',      # In stock
    'outofstock': 'Не',   # Out of stock
}

# Default values for missing fields
DEFAULTS = {
    'catalog_num': '',
    'name': '',
    'price': '0',
    'price_client': '0',
    'available': 'Не',
    'barcode': 'N/A',
    'brand': 'N/A',
    'category': '',
    'color': 'N/A',
}

# Output XML schema definition
# Each field: (xml_tag, required, use_cdata)
OUTPUT_SCHEMA = [
    ('catalog_num', True, False),
    ('name', True, True),         # CDATA
    ('price', True, False),
    ('price_client', True, False),
    ('available', False, False),
    ('barcode', False, True),     # CDATA
    ('brand', False, True),       # CDATA
    ('category', False, True),    # CDATA
    ('color', False, True),       # CDATA
]

# Root element name for output XML
OUTPUT_ROOT_ELEMENT = 'products'

# Product element name for output XML
OUTPUT_PRODUCT_ELEMENT = 'item'

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
    available = STOCK_MAPPING.get(quantity_label, DEFAULTS['available'])
    
    return {
        'catalog_num': product_data.get('catalog_num', DEFAULTS['catalog_num']),
        'name': product_data.get('name', DEFAULTS['name']),
        'price': product_data.get('price', DEFAULTS['price']),
        'price_client': product_data.get('price_client', DEFAULTS['price_client']),
        'available': available,
        'barcode': product_data.get('barcode', DEFAULTS['barcode']) or DEFAULTS['barcode'],
        'brand': product_data.get('brand', DEFAULTS['brand']) or DEFAULTS['brand'],
        'category': product_data.get('category', DEFAULTS['category']) or DEFAULTS['category'],
        'color': product_data.get('color', DEFAULTS['color']) or DEFAULTS['color'],
    }
