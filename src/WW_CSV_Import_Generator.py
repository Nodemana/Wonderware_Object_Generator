import tkinter as tk
from tkinter import filedialog
import pandas as pd
import sys
import os
import json
import tkinter as tk
from tkinter import simpledialog
from datetime import datetime

class Object_Set:
    def __init__(self, galaxy='none-specified', date='none-specified', json_dir='json/'):
        '''
        Constructor for Wonderware Object Set
        Params:\n
            galaxy: the name of the galaxy you're importing into.
            date: the creation date in format ie "31/01/2024 10:49:20 AM"
            json_dir: directory where JSON files are stored
        '''
        self.galaxy = galaxy
        self.date = date
        self.json_dir = json_dir
        self.object_instances = {}
        self.template_attributes = {}
        self.path = self.get_path()
        self.load_template_attributes()
        self.get_objects(self.path)

    def load_template_attributes(self):
        '''
        Loads all JSON files into memory.
        '''
        try:
            for file in os.listdir(self.json_dir):
                if file.endswith(".json"):
                    full_path = os.path.join(self.json_dir, file)
                    print(f"Loading JSON file: {full_path}")  # Print the file being loaded
                    with open(full_path, 'r') as f:
                        data = json.load(f)
                        self.template_attributes.update(data)
        except Exception as e:
            print(f"An error occurred while loading JSON files: {e}")

    def get_objects(self, path):
        '''
        Generates Objects From Spreadsheet.
        Params:
            path: path to the spreadsheet.
        '''
        print(f"Loading objects from Excel file: {path}")
        df = pd.read_excel(path)
        print(f"Loaded {len(df)} rows from the spreadsheet.")
        print(f'Loaded JSON Attributes: {self.template_attributes}')
        for index, row in df.iterrows():
            template_type = row['Template']
            #print(template_type)
            
            if template_type in self.template_attributes:
                print(template_type)
                attr_string, value_string = self.get_attr_value_strings(template_type, row)
                obj = TemplateBase(template_type, row['Tagname'], row['Area'], row['Short Description'], attr_string, value_string)
                if template_type not in self.object_instances:
                    self.object_instances[template_type] = []
                self.object_instances[template_type].append(obj)
                print(f"Object created: {obj}")

    def get_attr_value_strings(self, template_type, row):
        '''
        Generates attribute and value strings based on the template type and row data.
        Replaces values for :Tagname, Area, and ShortDesc with class field values from spreadsheet.
        '''
        attributes = self.template_attributes.get(template_type, {})
        values = []
        for attr in attributes.keys():
            if attr == ':Tagname':
                value_str = str(row.get('Tagname', '')).strip()
            elif attr == 'Area':
                value_str = str(row.get('Area', '')).strip()
            elif attr == 'ShortDesc':
                value_str = str(row.get('Short Description', '')).strip()
            else:
                # Use the default value from JSON or the value from the row, if specified
                value_str = str(row.get(attr, '') or attributes[attr])
            # Check if the value contains a comma
            if ',' in value_str:
                # Remove any existing quotes
                value_str = value_str.strip('"')
                # Re-enclose the value in quotes
                value_str = f'"{value_str}"'

            values.append(value_str)
        return ','.join(attributes.keys()), ','.join(values)


    def get_path(self):
        '''
        Prompts User for Path to an Excel Spreadsheet.
        '''
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title='Select the Excel spreadsheet', filetypes=[("Excel files", "*.xlsx *.xls")])
        root.destroy()
        
        # Convert the file path to an absolute path
        absolute_file_path = os.path.abspath(file_path) if file_path else None
        return absolute_file_path


    def set_json_dir(self, path):
        self.json_dir = path
        self.load_template_attributes()

    def generate_csv(self, output_path):
        '''
        Generates a CSV file formatted to be imported into ArchestrA.
        Params:
            output_path: Path where the CSV file will be saved.
        '''
        try:
            with open(output_path, 'w', newline='', encoding='utf-16') as csvfile:
                # Write the header
                csvfile.write(f'; Created on: {self.date} from Galaxy: {self.galaxy}\n\n')

                for template_type, instances in self.object_instances.items():
                    # Write the template type
                    csvfile.write(f'\n:TEMPLATE=${template_type}\n')

                    if instances:
                        # Write the column headers
                        headers = instances[0].attr_string.split(',')
                        csvfile.write(','.join(headers) + '\n')

                        # Write each instance
                        for instance in instances:
                            # Construct the row as a string
                            row = instance.value_string.split(',')
                            formatted_row = ','.join(row)
                            csvfile.write(formatted_row + '\n')
                print(f"CSV generated successfully at: {output_path}")
        except Exception as e:
            print(f"An error occurred while generating the CSV: {e}")

class TemplateBase:
    def __init__(self, template_type, tagname, area, shortdesc, attr_string, value_string):
        '''
        Constructor for Wonderware Base Object
        Params:\n
            template_type: object template
            tagname: the name of the object.
            area: within what area is the object to sit under.
            shortdesc: description of the object.
            attr_string: comma-separated string of attribute names.
            value_string: comma-separated string of corresponding values.
        '''
        self.template_type = template_type
        self.tagname = tagname
        self.area = area
        self.shortdesc = shortdesc
        self.attr_string = attr_string
        self.value_string = value_string

    def __repr__(self):
        return f"{self.__class__.__name__}(tagname='{self.tagname}', area='{self.area}', shortdesc='{self.shortdesc}', attr_string='{self.attr_string}', value_string='{self.value_string}')"




if __name__ == "__main__":
    # Set up the root Tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Prompt for the galaxy name
    galaxy_name = simpledialog.askstring("Input", "Enter the galaxy name:", parent=root)

    # Get the current date and time in the desired format
    current_date = datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')
    print(f"Current working directory: {os.getcwd()}")

    # Prompt for the JSON directory
    json_dir = filedialog.askdirectory(title="Select the directory of JSON files")
    print(f"Selected JSON directory: {json_dir}")

    # Make sure the user didn't cancel the directory selection
    if json_dir:
        # Create the Object_Set with the user input and current date
        
        generator = Object_Set(galaxy=galaxy_name, date=current_date, json_dir=os.path.abspath(json_dir))

        print(f"JSON directory set to: {generator.json_dir}")

        # Prompt the user to select the file path for saving the import.csv
        output_csv_path = filedialog.asksaveasfilename(
            title="Save import.csv",
            initialdir=os.path.expanduser('~'),  # Start at the user's home directory
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="import.csv"  # Suggest a default file name that will appear in the save dialog
        )
        
        # Check if the user provided a file path
        if output_csv_path:
            # Generate the CSV file
            generator.generate_csv(output_csv_path)
            print(f"File saved to: {output_csv_path}")  # Print the path where the file was saved for debugging
        else:
            print("File save operation canceled.")
    else:
        print("JSON directory selection was canceled.")
    
    # Clean up the Tkinter root window
    root.destroy()