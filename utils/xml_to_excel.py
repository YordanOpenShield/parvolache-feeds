import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Convert XML to Excel.')
    parser.add_argument('--xml', required=True, help='Input XML file name (from artifacts directory)')
    parser.add_argument('--excel', required=True, help='Output Excel file name (will be placed in artifacts directory)')
    args = parser.parse_args()

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    artifacts_dir = os.path.join(root_dir, 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    xml_path = os.path.join(artifacts_dir, args.xml + '.xml')
    excel_path = os.path.join(artifacts_dir, args.excel + '.xlsx')

    tree = ET.parse(xml_path)
    root = tree.getroot()

    rows = []
    for item in root.findall('item'):
        row = {}
        for child in item:
            row[child.tag] = child.text if child.text is not None else ''
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_excel(excel_path, index=False)

if __name__ == '__main__':
    main()
