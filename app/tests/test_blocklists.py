from app.blocklists import (
    refresh_all_blocklists,
    is_domain_blocked,
    _blocklists
)

# Run once before tests
def setup_module():
    if not _blocklists:
        refresh_all_blocklists()

def test_blocklists_loaded():
    assert len(_blocklists) == 6
    assert "adult" in _blocklists
    assert "malware" in _blocklists

def test_adult_content_blocked():
    assert is_domain_blocked("pornhub.com", ["adult"])

def test_gambling_blocked():
    assert is_domain_blocked("bet365.com", ["gambling"])

def test_safe_site_allowed():
    assert not is_domain_blocked("google.com", ["adult", "gambling"])

def test_mandatory_always_checked():
    # Malware should block even with empty categories
    # Pick a domain from your malware list sample
    malware_sample = list(_blocklists["malware"])[0]
    assert is_domain_blocked(malware_sample, [])

def test_specific_url_blocking():
    assert is_domain_blocked("custom-blocked.com", [], ["custom-blocked.com"])
    assert not is_domain_blocked("other.com", [], ["custom-blocked.com"])