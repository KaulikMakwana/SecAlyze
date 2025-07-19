# helpers/mimetype_map.py
# Provides a mapping from user-friendly aliases to standard MIME types for Secalyze CLI and template compatibility.

MIMETYPE_ALIASES = {
    'json': 'application/json',
    'text': 'text/plain',
    'xml': 'application/xml',
    'yaml': 'application/yaml',
    'yml': 'application/yaml',
    'x.enum': 'text/x.enum',
    'enum': 'text/x.enum',
    'plain': 'text/plain',
    # Add more aliases if needed
}

def resolve_mimetype(user_value: str) -> str:
    """
    Maps a user-provided value (from CLI or template) to a standard MIME type string.
    Returns the original value if not found in the aliases dict.
    """
    if not user_value:
        return 'text/plain'
    key = user_value.strip().lower()
    return MIMETYPE_ALIASES.get(key, user_value)

MIMETYPE_EXTENSIONS = {
    'application/json': '.json',
    'text/plain': '.txt',
    'application/xml': '.xml',
    'application/yaml': '.yaml',
    'text/x.enum': '.enum',
    'text/markdown': '.md',
}

# Accept aliases for extension as well
EXTENSION_ALIASES = {
    'json': '.json',
    'text': '.txt',
    'xml': '.xml',
    'yaml': '.yaml',
    'yml': '.yaml',
    'x.enum': '.enum',
    'enum': '.enum',
    'plain': '.txt',
    'md': '.md',
    'markdown': '.md',
}

def get_extension_for_mimetype(user_value: str) -> str:
    """
    Given a user value or MIME type, return the preferred extension (with dot).
    Defaults to .txt if not known.
    """
    if not user_value:
        return '.txt'
    key = user_value.strip().lower()
    # Try alias mapping first
    if key in EXTENSION_ALIASES:
        return EXTENSION_ALIASES[key]
    # Try MIME type mapping
    mimetype = resolve_mimetype(key)
    return MIMETYPE_EXTENSIONS.get(mimetype, '.txt')
