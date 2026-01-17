# test_blocklists.py
from app.blocklists import (
    refresh_all_blocklists,
    is_domain_blocked,
    _blocklists,
    MANDATORY_CATEGORIES,
    OPTIONAL_CATEGORIES
)

def test_blocklists():
    print("Loading blocklists...")
    refresh_all_blocklists()
    
    # Check what got loaded
    print("\n--- Loaded Categories ---")
    for cat, domains in _blocklists.items():
        print(f"{cat}: {len(domains)} domains")
    
    # Sample domains from each category
    print("\n--- Sample Domains ---")
    for cat, domains in _blocklists.items():
        sample = list(domains)[:3]
        print(f"{cat}: {sample}")
    
    # Test blocking logic
    print("\n--- Blocking Tests ---")
    test_cases = [
        ("pornhub.com", ["adult"], "should be blocked"),
        ("google.com", ["adult"], "should NOT be blocked"),
        ("bet365.com", ["gambling"], "should be blocked"),
        ("discord.com", ["chat"], "should be blocked"),
    ]
    
    for domain, categories, expected in test_cases:
        result = is_domain_blocked(domain, categories)
        status = "BLOCKED" if result else "ALLOWED"
        print(f"{domain} ({expected}): {status}")

if __name__ == "__main__":
    test_blocklists()