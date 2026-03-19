from __future__ import annotations

from datetime import datetime
from typing import Optional

def normalize_text(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    return " ".join(text.split()).strip()

def normalize_and_capitalize(text: Optional[str]) -> Optional[str]:
    normalized = normalize_text(text)
    if normalized is None:
        return None
    return normalized.capitalize()

def format_date_to_db(date_str: str) -> str:
    try:
        if "-" in date_str:
            parts = date_str.split("-")
            if len(parts[0]) == 4:
                return date_str
            formato = "%d-%m-%Y"
        elif "/" in date_str:
            formato = "%d/%m/%Y"
        else:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
            
        return datetime.strptime(date_str, formato).strftime("%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"Invalid date format: {date_str}")
