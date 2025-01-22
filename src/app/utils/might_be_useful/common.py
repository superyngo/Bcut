import hashlib
import re
from pathlib import Path
import json

def sanitize_string(value):
    # Remove non-printable and non-ASCII characters, except for common Chinese characters and punctuation
    if isinstance(value, str):
        return re.sub(r'[^\x20-\x7E\u4E00-\u9FFF\u3000-\u303F]', '', value)
    return value

def convert_roc_to_western(roc_date: str = "") -> str:
    if roc_date == "":
        return ""
    # Step 1: Eliminate all non-numeric characters except "/" and "-"
    cleaned_date = re.sub(r'[^\d/-]', '', roc_date)
    # Step 2: Extract the first 3 characters (ROC year) and convert to Western year
    roc_year = int(cleaned_date[:3])
    western_year = str(roc_year + 1911)
    # Step 3: Combine Western year with the remaining part of the ROC date string
    western_date = western_year + cleaned_date[3:]
    return western_date

def create_sha256_hash(data):
    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()
    
    # Encode the input data to bytes (if it's a string) and update the hash object
    sha256_hash.update(data.encode('utf-8'))
    
    # Get the hexadecimal representation of the hash
    return sha256_hash.hexdigest()

def load_assignment(path: Path):
    with open(path, 'r') as f:
        return json.load(f)