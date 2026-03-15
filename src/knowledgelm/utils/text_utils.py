"""Utility functions for text processing."""


def pluralize(text: str, count: int = 2) -> str:
    """
    Pluralize a string based on the provided count.
    
    If count is 1, returns the original text.
    Otherwise, applies basic pluralization rules.
    """
    if count == 1:
        return text
    
    if text.endswith("y"):
        return f"{text[:-1]}ies"
    
    return f"{text}s"
