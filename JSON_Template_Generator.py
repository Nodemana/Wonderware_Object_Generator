import json
import csv
import os

def generate_json_from_csv(csv_path):
    with open(csv_path, 'r', encoding='utf-16') as file:
        reader = csv.reader(file)
        lines = list(reader)

    # Find the line containing the template name
    template_name = None
    for i, line in enumerate(lines):
        if line and line[0].startswith(":TEMPLATE=$"):
            template_name = line[0].split('$')[1]
            attributes_line = lines[i + 1]  # Attributes are in the next line
            defaults_line = lines[i + 2]   # Defaults are in the line after attributes
            break

    if not template_name:
        raise ValueError("Template name not found in the file.")

    # Ensure each attribute has a corresponding default value
    attribute_defaults = {}
    for idx, attr in enumerate(attributes_line):
        default_value = defaults_line[idx] if idx < len(defaults_line) else ''
        attribute_defaults[attr] = default_value

    # Construct the JSON object
    template_json = {template_name: attribute_defaults}

    # Save the JSON object to a file
    with open(f"json/{template_name}.json", 'w', encoding='utf-8') as json_file:
        json.dump(template_json, json_file, indent=4)

    return template_json

def generate_jsons_from_directory(directory_path):
    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a CSV file
        if filename.endswith('.csv'):
            csv_path = os.path.join(directory_path, filename)
            try:
                template_config_json = generate_json_from_csv(csv_path)
                print(f"Generated JSON for {filename}:")
                print(json.dumps(template_config_json, indent=4))
            except Exception as e:
                print(f"An error occurred processing {filename}: {e}")

# Path to the directory containing CSV files
directory_path = 'csvs'

# Generate JSONs from CSVs in the directory
generate_jsons_from_directory(directory_path)
