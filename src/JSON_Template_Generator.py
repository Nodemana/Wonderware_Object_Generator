import tkinter as tk
from tkinter import filedialog
import json
import csv
import os

def generate_json_from_csv(csv_path, json_directory):
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
    json_filename = f"{template_name}.json"
    json_path = os.path.join(json_directory, json_filename)

    # Save the JSON object to a file
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(template_json, json_file, indent=4)

    return template_json

def generate_jsons_from_directory(directory_path, json_directory):
    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a CSV file
        if filename.endswith('.csv'):
            csv_path = os.path.join(directory_path, filename)
            try:
                template_config_json = generate_json_from_csv(csv_path, json_directory)
                print(f"Generated JSON for {filename}:")
                print(json.dumps(template_config_json, indent=4))
            except Exception as e:
                print(f"An error occurred processing {filename}: {e}")

# Prompt for the CSV directory
csv_directory = filedialog.askdirectory(title="Select the directory of CSV files")
print(f"Selected CSV directory: {csv_directory}")

# Prompt for the CSV directory
json_directory = filedialog.askdirectory(title="Select the directory to store JSON files")
print(f"Selected JSON directory: {json_directory}")

# Generate JSONs from CSVs in the directory
generate_jsons_from_directory(csv_directory, json_directory)
