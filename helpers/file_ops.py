#!/usr/bin/python3.13
from helpers.colours import INFO, SUCCESS, FAILED, ERROR, TEXT, RESET

def save_content(content, filename, mode='w'):
    """Save content to a file."""
    try:
        with open(filename, mode) as file:
            file.write(content)
        print(f"{SUCCESS}[+] Successfully saved to {filename}{RESET}")
    except Exception as e:
        print(f"{ERROR}[?] Failed to save content: {e}{RESET}")

def read_file_content(file):
    """Read content from a file."""
    try:
        with open(file, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"{ERROR}[?] Error reading file: {e}{RESET}")
        return None