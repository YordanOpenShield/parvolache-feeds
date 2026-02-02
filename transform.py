#!/usr/bin/env python3
"""
Static XML Feed Transformer
Fetches a source XML feed and transforms it into partner-specific XML structures.
Publishes the results as static XML files.

Usage:
    python transform.py [PARTNER_NAME]
    
    If PARTNER_NAME is omitted, defaults to 'ozone'.
    
Examples:
    python transform.py              # Transform ozone feed
    python transform.py ozone        # Transform ozone feed (explicit)
    python transform.py amazon       # Transform amazon feed (if configured)
"""

import sys
import logging
import importlib
from pathlib import Path
from datetime import datetime

import requests
from lxml import etree

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_partner_config(partner_name: str):
    """
    Dynamically load partner configuration module.
    
    Args:
        partner_name: Name of the partner (must have a config in partners/{name}/config.py)
        
    Returns:
        The partner config module
        
    Raises:
        SystemExit: If partner config cannot be loaded
    """
    logger.info(f"Loading configuration for partner: {partner_name}")
    try:
        config = importlib.import_module(f"partners.{partner_name}.config")
        logger.info(f"Successfully loaded {partner_name} configuration")
        return config
    except ImportError as e:
        logger.error(f"Failed to load partner config: {e}")
        logger.error(f"Ensure partners/{partner_name}/config.py exists")
        sys.exit(1)


def fetch_source_feed(url: str) -> str:
    """
    Fetch the source XML feed from the configured URL.
    
    Args:
        url: The URL of the source feed
        
    Returns:
        The XML content as a string
        
    Raises:
        SystemExit: If the feed is unreachable
    """
    logger.info(f"Fetching source feed from: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully fetched feed ({len(response.content)} bytes)")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch source feed: {e}")
        sys.exit(1)


def parse_xml(content: str) -> etree._Element:
    """
    Safely parse XML content.
    
    Args:
        content: The XML content as a string
        
    Returns:
        The root element of the parsed XML tree
        
    Raises:
        SystemExit: If XML parsing fails
    """
    logger.info("Parsing source XML...")
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.fromstring(content.encode("utf-8"), parser=parser)
        logger.info("Successfully parsed source XML")
        return root
    except etree.XMLSyntaxError as e:
        logger.error(f"XML parsing failed: {e}")
        sys.exit(1)


def extract_text(element: etree._Element, xpath: str, default: str = "", namespaces: dict = None) -> str:
    """
    Extract text from XML element using XPath.
    
    Args:
        element: The XML element to search within
        xpath: The XPath expression
        default: Default value if not found
        namespaces: Optional namespace dictionary for XPath
        
    Returns:
        The extracted text, stripped and non-empty, or the default value
    """
    try:
        kwargs = {"namespaces": namespaces} if namespaces else {}
        result = element.xpath(xpath, **kwargs)
        if result:
            text = str(result[0]).strip() if isinstance(result[0], str) else ""
            return text if text else default
    except Exception:
        pass
    return default


def transform_feed(source_root: etree._Element, config) -> etree._Element:
    """
    Transform source XML into partner-specific structure.
    
    Args:
        source_root: The root element of the source XML
        config: The partner configuration module
        
    Returns:
        The root element of the transformed XML tree
    """
    logger.info("Transforming feed to partner schema...")
    
    # Create root element
    products_root = etree.Element(config.OUTPUT_ROOT_ELEMENT)
    
    # Find all products in source using namespace-aware XPath
    product_elements = source_root.xpath("//sc:Products/sc:Product", namespaces=config.SOURCE_NAMESPACE)
    
    if not product_elements:
        logger.warning("No products found in source feed")
        return products_root
    
    logger.info(f"Found {len(product_elements)} products to transform")
    
    for idx, product in enumerate(product_elements, 1):
        try:
            # Extract data using partner-specific field mappings
            product_data = {}
            for field_name, xpath_expr in config.FIELD_MAPPINGS.items():
                product_data[field_name] = extract_text(
                    product, 
                    xpath_expr, 
                    config.DEFAULTS.get(field_name, ""),
                    config.SOURCE_NAMESPACE
                )
            
            # Apply partner-specific transformation logic
            output_fields = config.transform_product(product_data)
            
            # Validate required fields
            missing_required = []
            for field_info in config.OUTPUT_SCHEMA:
                field_name = field_info[0]
                required = field_info[1]
                if required and not output_fields.get(field_name):
                    missing_required.append(field_name)
            
            if missing_required:
                continue
            
            # Create product element
            product_elem = etree.SubElement(products_root, config.OUTPUT_PRODUCT_ELEMENT)
            
            # Add output fields with optional CDATA support
            for field_info in config.OUTPUT_SCHEMA:
                field_name = field_info[0]
                use_cdata = field_info[2] if len(field_info) > 2 else False
                
                if field_name in output_fields:
                    field_elem = etree.SubElement(product_elem, field_name)
                    value = output_fields[field_name]
                    
                    if use_cdata and value:
                        # Add CDATA section
                        field_elem.text = etree.CDATA(value)
                    else:
                        field_elem.text = value
            
        except Exception as e:
            logger.debug(f"Error processing product {idx}: {e}")
            continue
    
    logger.info(f"Successfully transformed {len(products_root)} products")
    return products_root


def write_output(root: etree._Element, output_path: Path) -> None:
    """
    Write the transformed XML to the output file.
    
    Args:
        root: The root element of the XML tree
        output_path: The path where the output file should be written
    """
    logger.info(f"Writing output to: {output_path}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Write XML with proper encoding and declaration
        tree = etree.ElementTree(root)
        tree.write(
            str(output_path),
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
        )
        
        file_size = output_path.stat().st_size
        logger.info(f"Successfully wrote output ({file_size} bytes)")
    except IOError as e:
        logger.error(f"Failed to write output file: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    # Get partner name from command line or use default
    partner_name = sys.argv[1] if len(sys.argv) > 1 else "ozone"
    
    # Load partner configuration
    config = load_partner_config(partner_name)
    
    # Determine output file path
    output_file = Path(__file__).parent / "output" / partner_name / "partner.xml"
    
    logger.info("=" * 60)
    logger.info("Starting XML Feed Transformation")
    logger.info(f"Partner: {partner_name}")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    try:
        # Fetch source feed
        source_content = fetch_source_feed(config.SOURCE_FEED_URL)
        
        # Parse source XML
        source_root = parse_xml(source_content)
        
        # Transform to partner schema
        transformed_root = transform_feed(source_root, config)
        
        # Write output
        write_output(transformed_root, output_file)
        
        logger.info("=" * 60)
        logger.info("✓ Feed transformation completed successfully")
        logger.info("=" * 60)
        
    except SystemExit as e:
        # Re-raise SystemExit to preserve exit code
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
