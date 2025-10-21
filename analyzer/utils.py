import hashlib
from typing import Dict, Any
import re


class NaturalLanguageParseError(Exception):
    pass


class NaturalLanguageConflictError(Exception):
    pass

def analyze_string(input_string: str) -> Dict[str, Any]:

    raw = input_string
    normalised = raw.strip().replace(" ", "").lower()
    length = len(raw.strip())
    is_palindrome = normalised == normalised[::-1]
    unique_characters = len(set(normalised))
    word_count = len(raw.split())
    character_frequency_map = {}
    for char in normalised:
        if char in character_frequency_map:
            character_frequency_map[char] += 1
        else:
            character_frequency_map[char] = 1
    sha256_hash = hashlib.sha256(normalised.encode('utf-8')).hexdigest()
    return {
        "value": raw,
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": character_frequency_map
    }


def parse_bool(value: str):
    if value.lower() in ("1", "true", "t", "yes", "y"):
        return True
    if value.lower() in ("0", "false", "f", "no", "n"):
        return False
    raise ValueError("Invalid boolean")

def parse_int(value: str):
    try:
        return int(value)
    except ValueError:
        raise ValueError("Invalid integer")


def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """Very small heuristic parser that converts a natural language query into filter dict.

    Returns a dict with parsed_filters. Raises NaturalLanguageParseError if it can't parse.
    Raises NaturalLanguageConflictError when parsed filters are contradictory.
    """
    if not query or not isinstance(query, str):
        raise NaturalLanguageParseError("Empty or invalid query")

    q = query.lower()
    parsed = {}

    if 'single word' in q or 'one word' in q or 'single-word' in q:
        parsed['word_count'] = 1

    if 'palindrom' in q:  
        parsed['is_palindrome'] = True

    m = re.search(r'longer than (\d+)', q)
    if m:
        n = int(m.group(1))
        parsed['min_length'] = n + 1

    m = re.search(r'shorter than (\d+)', q)
    if m:
        n = int(m.group(1))
        parsed['max_length'] = n - 1 if n > 0 else 0

    m = re.search(r'at least (\d+)', q)
    if m:
        parsed['min_length'] = int(m.group(1))

    m = re.search(r'more than (\d+) characters', q)
    if m:
        parsed['min_length'] = int(m.group(1)) + 1

    m = re.search(r'contains(?: the)? (?:letter |char |character )?([a-z])', q)
    if m:
        parsed['contains_character'] = m.group(1)

    if 'first vowel' in q:
        parsed['contains_character'] = 'a'

    m = re.search(r'containing the letter ([a-z])', q)
    if m:
        parsed['contains_character'] = m.group(1)

    if not parsed:
        raise NaturalLanguageParseError('Unable to parse natural language query')

    if 'min_length' in parsed and 'max_length' in parsed and parsed['min_length'] > parsed['max_length']:
        raise NaturalLanguageConflictError('Parsed min_length is greater than max_length')

    return {'original': query, 'parsed_filters': parsed}