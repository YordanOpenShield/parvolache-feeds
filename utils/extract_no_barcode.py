import xml.etree.ElementTree as ET
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Extract items without barcode from partner XML.')
    parser.add_argument('--partner', required=True, help='Partner name (used to find input XML in output/<partner>/partner.xml)')
    parser.add_argument('--out', required=True, help='Output file name (will be placed in artifacts directory)')
    args = parser.parse_args()

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(root_dir, 'output', args.partner, 'partner.xml')
    artifacts_dir = os.path.join(root_dir, 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    output_path = os.path.join(artifacts_dir, args.out + '.xml')

    tree = ET.parse(input_path)
    root = tree.getroot()

    output_root = ET.Element('items')

    for item in root.findall('item'):
        barcode = item.find('barcode')
        if barcode is not None and barcode.text == 'N/A':
            output_root.append(item)

    output_tree = ET.ElementTree(output_root)
    output_tree.write(output_path, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    main()
