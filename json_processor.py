"""Processes JSON files.
"""

import json
from typing import Tuple, Optional, List, Tuple

ENCODING = "utf-8"

def read_json_file(filename: str) -> dict:
    """Reads a JSON file and retrieves its content.
    Parameter:
    -- filename: str
    ---- The name of the JSON file.
    Return value: dict
    -- The dictionary of JSON data.
    """
    with open(filename, "r", encoding=ENCODING) as file:
        return json.loads(file.read())

def write_json_file(filename: str, json_content: dict) -> None:
    """Reads dictionary of JSON content and saves it to a JSON file.
    Parameter:
    -- filename: str
    ---- The name of the JSON file.
    -- json_content: dict
    ---- The content to be saved to the JSON file.
    """
    with open(filename, "w", encoding=ENCODING) as file:
        file.write(json.dumps(json_content, indent=4))