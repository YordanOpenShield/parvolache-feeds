"""
Google Merchant Partner Configuration

Generates RSS 2.0 XML feed following Google Merchant Center specification.
Maps Seliton SummerCart fields to Google Shopping attributes.

Feed specification: https://support.google.com/merchants/answer/7052112
"""

import re
from lxml import etree

# =============================================================================
# SOURCE FEED CONFIGURATION
# =============================================================================

SOURCE_FEED_URL = (
    "https://parvolache.com/module.php"
    "?ModuleName=com.seliton.superxmlexport"
    "&Username=teocombg"
    "&Domain=parvolache.com"
    "&Signature=e2ddf641b1cb647ddfe4d1d11abbcd7ed7a13f7a"
    "&DealerAccountType=0"
)

# XML namespace used in source feed (SummerCart dealer schema)
SOURCE_NAMESPACE = {
    'sc': 'http://schemas.summercart.com/dealer/v1',
}

# =============================================================================
# FIELD MAPPINGS (Seliton XPath -> internal field names)
# =============================================================================

FIELD_MAPPINGS = {
    'id': './/sc:ProductID/text()',
    'catalog_num': './/sc:ProductCode/text()',
    'title': './/sc:ProductName/sc:BG/text()',
    'description': './/sc:ProductDescription/sc:BG/text()',
    'description_detailed': './/sc:ProductDetailedDescription/sc:BG/text()',
    'link': './/sc:ProductUrl/text()',
    'price': './/sc:ProductPrice/text()',
    'price_wholesale': './/sc:ProductDistributorPrice/text()',
    'quantity_label': './/sc:ProductQuantityLabel/text()',
    'barcode': './/sc:ProductBarcode/text()',
    'brand': './/sc:BrandName/sc:BG/text()',
    'category_branch': './/sc:Category/sc:CategoryBranch/sc:BG/text()',
    'category_name': './/sc:Category/sc:CategoryName/sc:BG/text()',
    'weight': './/sc:ProductWeight/text()',
    'currency': './/sc:ProductPrice/@currencycode',
}

# =============================================================================
# DEFAULT VALUES
# =============================================================================

DEFAULTS = {
    'id': '',
    'catalog_num': '',
    'title': '',
    'description': '',
    'description_detailed': '',
    'link': '',
    'price': '0',
    'price_wholesale': '0',
    'available': 'out_of_stock',
    'barcode': '',
    'brand': 'Първолаче',
    'category_branch': '',
    'category_name': '',
    'weight': '',
    'currency': 'EUR',
}

# =============================================================================
# MAPPING DICTIONARIES
# =============================================================================

# Availability: SummerCart quantity_label -> Google Merchant availability
AVAILABILITY_MAPPING = {
    'InStock': 'in_stock',
    'OutOfStock': 'out_of_stock',
    'PreOrder': 'preorder',
    'BackOrder': 'backorder',
}

# Google Product Category: Seliton category name -> Google category ID
# Based on Google's taxonomy (https://www.google.com/basepages/producttype/taxonomy.en-US.txt)
GOOGLE_CATEGORY_MAPPING = {
    'Раници': '1097',             # Apparel & Accessories > Backpacks
    'Ученически раници': '1097',  # Same as above
    'Комплекти': '965',           # Office Supplies > Classroom & Teaching Supplies
    'Цветни моливи': '4985',      # Arts & Entertainment > Art & Craft Kits > Coloring & Drawing Kits
    'Флумастери': '4992',         # Arts & Entertainment > Hobbies & Creative Arts > Drawing & Writing Supplies > Markers & Highlighters
    'Боички': '505378',           # Arts & Entertainment > Hobbies & Creative Arts > Drawing & Writing Supplies > Paints & Paint Sets
    'Тетрадки': '503739',         # Office Supplies > Paper & Notebooks > Notebooks & Notepads
    'Лепила': '503740',           # Office Supplies > Office Instruments > Adhesives & Fasteners > Glues & Pastes
    'Ножици': '503741',           # Office Supplies > Office Instruments > Scissors & Trimmers
    'Химикали': '4035',           # Office Supplies > Writing Instruments > Pens
    'Моливи': '6020',             # Office Supplies > Writing Instruments > Pencils
    'Гуми': '503755',             # Office Supplies > Office Instruments > Writing Accessories > Erasers
    'Линии': '503739',            # Office Supplies > Paper & Notebooks > Notebooks & Notepads
    'Канцеларски материали': '503740',  # General office supplies
    'Детски книги': '12217',      # Media > Books > Children's Books
    'Игри и играчки': '166',      # Toys & Games
    'Пластелин': '505378',        # Arts & Entertainment > Hobbies & Creative Arts > Drawing & Writing Supplies > Paints & Paint Sets
}

# =============================================================================
# OUTPUT SCHEMA (used for required-field validation only)
# build_output_xml() handles the actual XML construction below.
# =============================================================================

OUTPUT_SCHEMA = [
    ('g:id', True),
    ('g:title', True),
    ('g:link', True),
    ('g:price', True),
    ('g:availability', True),
]

# Google namespace for output XML (handled via nsmap in build_output_xml)


# =============================================================================
# EXTRACTION & TRANSFORMATION
# =============================================================================

def extract_additional_fields(product_element, product_data):
    """
    Extract fields that need special XPath handling (multiple values, etc.).

    Args:
        product_element: The lxml Element for a single product from source XML.
        product_data: Dict with basic field values already extracted.

    Returns:
        Updated product_data dict with additional fields.
    """
    ns = SOURCE_NAMESPACE

    # --- Multiple product images ---
    image_paths = product_element.xpath(
        './/sc:ProductImages/sc:ProductImage/sc:ImagePath/text()',
        namespaces=ns,
    )
    # Normalise to HTTPS
    product_data['image_paths'] = [
        img.replace('http://', 'https://', 1) if img.startswith('http://') else img
        for img in (image_paths or [])
    ]

    # --- Sale price from wholesale prices ---
    sale_prices = product_element.xpath(
        './/sc:WholesalePrices/sc:WholesalePrice/sc:WholesalePriceAmount/text()',
        namespaces=ns,
    )
    product_data['sale_price'] = sale_prices[0] if sale_prices else ''

    return product_data


def transform_product(product_data):
    """
    Transform extracted product data into Google Merchant output fields.

    Args:
        product_data: Dict with keys matching FIELD_MAPPINGS and extract_additional_fields.

    Returns:
        Dict with Google Merchant attribute names and formatted values.
    """
    # --- Availability ---
    quantity_label = (product_data.get('quantity_label') or '').strip()
    availability = AVAILABILITY_MAPPING.get(quantity_label, DEFAULTS['available'])

    # --- Brand ---
    brand = (product_data.get('brand') or '').strip()
    if not brand:
        brand = DEFAULTS['brand']

    # --- Description (prefer detailed, fallback to short) ---
    description = (product_data.get('description_detailed') or '').strip()
    if not description:
        description = (product_data.get('description') or '').strip()
    if description:
        # Strip HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        # Collapse whitespace
        description = re.sub(r'\s+', ' ', description).strip()

    # --- Prices ---
    price = (product_data.get('price') or DEFAULTS['price']).strip()
    sale_price_candidate = (product_data.get('sale_price') or '').strip()
    wholesale = (product_data.get('price_wholesale') or '').strip()

    # Use the actual currency from the source feed (EUR, BGN, etc.)
    currency = (product_data.get('currency') or DEFAULTS['currency']).strip()

    # Use wholesale as sale price if no explicit sale price and they differ
    if not sale_price_candidate and wholesale and wholesale != price:
        sale_price_candidate = wholesale

    price_formatted = f"{price} {currency}"
    sale_price_formatted = f"{sale_price_candidate} {currency}" if sale_price_candidate and sale_price_candidate != price else ''

    # --- Product type (hierarchy) ---
    category_branch = (product_data.get('category_branch') or '').strip()
    if category_branch:
        parts = category_branch.split('|')
        if not parts[0].startswith('Училище'):
            product_type = 'Училище > ' + ' > '.join(parts)
        else:
            product_type = ' > '.join(parts)
    else:
        product_type = ''

    # --- Google product category ---
    category_name = (product_data.get('category_name') or '').strip()
    google_category = GOOGLE_CATEGORY_MAPPING.get(category_name, '')

    # --- Weight ---
    weight = (product_data.get('weight') or '').strip()
    if weight:
        weight = f"{weight} kg"

    # --- Barcode / GTIN ---
    barcode = (product_data.get('barcode') or '').strip()
    has_gtin = bool(barcode)

    # --- Link (force HTTPS) ---
    link = (product_data.get('link') or '').strip()
    if link.startswith('http://'):
        link = link.replace('http://', 'https://', 1)

    # --- Images ---
    image_paths = product_data.get('image_paths', [])
    main_image = image_paths[0] if image_paths else ''
    additional_images = image_paths[1:11]  # Google allows up to 10 additional images

    return {
        'g:id': product_data.get('id', DEFAULTS['id']),
        'g:title': product_data.get('title', DEFAULTS['title']),
        'g:description': description,
        'g:link': link,
        'g:image_link': main_image,
        'g:additional_image_link': additional_images,
        'g:availability': availability,
        'g:price': price_formatted,
        'g:sale_price': sale_price_formatted,
        'g:condition': 'new',
        'g:brand': brand,
        'g:mpn': product_data.get('catalog_num', DEFAULTS['catalog_num']),
        'g:gtin': barcode if has_gtin else '',
        'g:identifier_exists': 'FALSE' if not has_gtin else 'TRUE',
        'g:product_type': product_type,
        'g:google_product_category': google_category,
        'g:shipping_weight': weight,
        'g:custom_label_0': '',       # Season — populate via config later
        'g:custom_label_1': '',       # Margin tier
        'g:custom_label_2': '',       # Bestseller flag
        'g:custom_label_3': brand,    # Manufacturer / brand
        'g:custom_label_4': '',       # Price range
    }


# =============================================================================
# OUTPUT XML BUILDER
# =============================================================================

def build_output_xml(products_data, config):
    """
    Build a Google Merchant RSS 2.0 feed from the transformed product data.

    Produces:
        <rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
          <channel>
            <title>...</title>
            <link>...</link>
            <description>...</description>
            <item>...</item>
          </channel>
        </rss>

    Args:
        products_data: List of dicts returned by transform_product().
        config: The partner config module.

    Returns:
        Root <rss> etree.Element.
    """
    # Root element with namespace map — ensures <g:> prefix and xmlns:g
    # declaration on the root, not repeated on every child.
    rss = etree.Element(
        'rss',
        version='2.0',
        nsmap={'g': 'http://base.google.com/ns/1.0'},
    )

    channel = etree.SubElement(rss, 'channel')

    # ── Channel metadata ──────────────────────────────────────────────
    _text_elem(channel, 'title', 'Книжарница Първолаче')
    _text_elem(channel, 'link', 'https://parvolache.com')
    _text_elem(channel, 'description', 'Ученически пособия и канцеларски материали')

    # ── Items ─────────────────────────────────────────────────────────
    g_ns = 'http://base.google.com/ns/1.0'

    for fields in products_data:
        item = etree.SubElement(channel, 'item')

        # Plain-text fields
        for tag in ('id', 'title', 'link', 'availability', 'price',
                     'condition', 'brand', 'mpn', 'gtin', 'identifier_exists',
                     'product_type', 'google_product_category', 'shipping_weight',
                     'custom_label_0', 'custom_label_1', 'custom_label_2',
                     'custom_label_3', 'custom_label_4', 'sale_price'):
            key = f'g:{tag}'
            value = fields.get(key)
            if value:
                elem = etree.SubElement(item, f'{{{g_ns}}}{tag}')
                elem.text = str(value)

        # CDATA-wrapped fields
        for tag in ('description',):
            key = f'g:{tag}'
            value = fields.get(key)
            if value:
                elem = etree.SubElement(item, f'{{{g_ns}}}{tag}')
                elem.text = etree.CDATA(str(value))

        # Main image
        main_image = fields.get('g:image_link', '')
        if main_image:
            elem = etree.SubElement(item, f'{{{g_ns}}}image_link')
            elem.text = str(main_image)

        # Additional images (up to 10)
        additional_images = fields.get('g:additional_image_link', [])
        if isinstance(additional_images, (list, tuple)):
            for img_url in additional_images[:10]:
                if img_url:
                    elem = etree.SubElement(item, f'{{{g_ns}}}additional_image_link')
                    elem.text = str(img_url)

    return rss


# ── Internal helpers ────────────────────────────────────────────────

def _text_elem(parent, tag, text):
    """Create a text child element."""
    elem = etree.SubElement(parent, tag)
    elem.text = text
    return elem
