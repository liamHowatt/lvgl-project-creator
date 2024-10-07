#!/usr/bin/env python3

import json
import requests
from jsonschema import validate, ValidationError

schema_individual = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "maintainer": {"type": "string"},
        "hostOperatingsystem": {
            "type": "array",
            "items": {"type": "string"}
        },
        "environment": {
            "type": "array",
            "items": {"type": "string"}
        },
        "hardware": {
            "type": "object",
            "properties": {
                "chipVendor": {"type": "string"},
                "manufacturer": {"type": "string"},
                "specs": {
                    "type": "object",
                    "properties": {
                        "MCU": {"type": "string"},
                        "RAM": {"type": "string"},
                        "Flash": {"type": "string"},
                        "GPU": {"type": ["string", "null"]},
                        "Resolution": {"type": "string"},
                        "Display Size": {"type": "string"},
                        "Interface": {"type": "string"},
                        "Color Depth": {"type": "string"},
                        "Technology": {"type": "string"},
                        "DPI": {"type": "string"},
                        "Touch Pad": {"type": "string"}
                    },
                    "required": ["MCU", "RAM", "Flash"]
                }
            },
            "required": ["chipVendor", "manufacturer", "specs"]
        },
        "description": {"type": "string"},
        "shortDescription": {"type": "string"},
        "urlToClone": {"type": "string"},
        "logo": {"type": "string"},
        "branches": {
            "type": "array",
            "items": {"type": "string"}
        },
        "settings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "label": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "value": {"type": "string"},
                                "default": {"type": "string", "enum": ["true", "false"], "default": "false"}
                            },
                            "required": ["name", "value"]
                        }
                    },
                    "actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ifValue": {"type": "string"},
                                "toAppend": {"type": "string"},
                                "toReplace": {"type": "string"},
                                "newContent": {"type": "string"},
                                "filePath": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["type", "label", "options"]
            }
        }
    },
    "required": ["name", "maintainer", "hostOperatingsystem", "environment", "description", "shortDescription", "urlToClone", "logo", "branches", "settings"]
}

schema_whole = {
   "type": "array",
    "items": schema_individual
}

# Function to validate JSON against the schema
def validate_json(json_data, schema):
    try:
        validate(instance=json_data, schema=schema)
        print("JSON is valid")
        return True
    except ValidationError as e:
        print(f"JSON validation error: {e.message}")
        if e.path:
            print(f"Error location: {' -> '.join(map(str, e.path))}")
        else:
            print("Error location: Root of the document")
        return False

# Function to fetch JSON content from a URL
def fetch_json(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

# List to hold all the JSON content
all_json_data = []

# Read the file containing URLs to JSON files
with open('manifests', 'r') as file:
    urls = file.readlines()

# Fetch and concatenate JSON data from each URL
for url in urls:
    url = url.strip()  # Remove any extra whitespace or newlines
    if url:  # Ensure the URL is not empty
        print(f"Fetching {url}")
        try:
            json_data = fetch_json(url)
            validate_json(json_data, schema_individual)  # Validate each JSON fetched
            all_json_data.append(json_data)  # Append if valid
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
        except ValidationError as e:
            print(f"Validation failed for {url}: {e.message}")


print("Validating the concatenated JSON")
valid = validate_json(all_json_data, schema_whole)
if valid:
    # Save the concatenated JSON data to a new file
    with open('manifest_all_v1_1.json', 'w') as outfile:
        json.dump(all_json_data, outfile, indent=4)

    print("All JSON data has been concatenated and saved to 'manifest_all.json'.")
else:
    print("Error: the concatenated JSON is invalid") 
