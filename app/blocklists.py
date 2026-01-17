import gzip
import requests
from pathlib import Path
from typing import Set
import os

CACHE_DIR = Path("./blocklist_cache")
BLOCKLIST_BASE_URL = "https://raw.githubusercontent.com/olbat/ut1-blacklists/master/blacklists"

# Always enabled (security)
MANDATORY_CATEGORIES = {
    "malware": "malware/domains"  # includes phishing
}

# Parent-controlled
OPTIONAL_CATEGORIES = {
    "adult": "adult/domains.gz",
    "gambling": "gambling/domains", 
    "violence": ["agressif/domains", "dangerous_material/domains"],
    "games": "games/domains",
    "chat": "chat/domains"
}

# In-memory cache
_blocklists: dict[str, Set[str]] = {}

def download_and_decompress(url: str) -> Set[str]:
    """Download and decompress blocklist, return set of domains"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    if url.endswith('.gz'):
        content = gzip.decompress(response.content).decode('utf-8')
    else:
        content = response.text
    
    return {line.strip() for line in content.splitlines() if line.strip()}

def load_category_blocklist(category: str, sources) -> Set[str]:
    """Load domains from single or multiple source files"""
    domains = set()
    
    # Handle both single string and list of strings
    source_list = [sources] if isinstance(sources, str) else sources
    
    for source in source_list:
        url = f"{BLOCKLIST_BASE_URL}/{source}"
        domains.update(download_and_decompress(url))
    
    return domains

def refresh_all_blocklists() -> None:
    """Download and cache all blocklists on startup"""
    global _blocklists
    
    CACHE_DIR.mkdir(exist_ok=True)
    
    # Load mandatory lists
    for category, sources in MANDATORY_CATEGORIES.items():
        print(f"Loading mandatory: {category}")
        _blocklists[category] = load_category_blocklist(category, sources)
    
    # Load optional lists
    for category, sources in OPTIONAL_CATEGORIES.items():
        print(f"Loading optional: {category}")
        _blocklists[category] = load_category_blocklist(category, sources)
    
    print(f"Loaded {len(_blocklists)} blocklists")

def is_domain_blocked(domain: str, enabled_categories: list[str], specific_urls: list[str] = None) -> bool:
    """Check if domain is blocked by mandatory categories, enabled categories, or specific URLs"""
    # Always check mandatory
    for category in MANDATORY_CATEGORIES.keys():
        if domain in _blocklists.get(category, set()):
            return True
    
    # Check enabled optional categories
    for category in enabled_categories:
        if domain in _blocklists.get(category, set()):
            return True
    
    # Check specific blocked URLs
    if specific_urls and domain in specific_urls:
        return True
    
    return False